import os
import json
import base64
import datetime
import streamlit as st
from PIL import Image
import io

# Page Config
st.set_page_config(
    page_title="BlueTalk - WhatsApp Style Messenger",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="expanded"
)

# WhatsApp-specific Theme Styling Injection
st.markdown("""
    <style>
    /* Global WhatsApp Light Theme Background */
    .main { background-color: #efeae2; }
    
    /* Hide default Streamlit top padding and footer */
    header { visibility: hidden; }
    footer { visibility: hidden; }
    
    /* WhatsApp Chat Header bar */
    .wa-header {
        background-color: #00a884;
        color: white;
        padding: 12px 16px;
        border-radius: 8px 8px 0 0;
        display: flex;
        align-items: center;
        font-family: Helvetica, Arial, sans-serif;
        font-weight: 500;
        font-size: 1.1rem;
        margin-bottom: 0px;
    }
    
    /* WhatsApp Chat Container Wallpaper */
    .wa-chat-container {
        background-color: #efeae2;
        background-image: radial-gradient(#d1dbd5 0.75px, transparent 0.75px), radial-gradient(#d1dbd5 0.75px, #efeae2 0.75px);
        background-size: 30px 30px;
        background-position: 0 0, 15px 15px;
        padding: 20px 10px;
        border-radius: 0 0 8px 8px;
        min-height: 400px;
        max-height: 550px;
        overflow-y: auto;
    }
    
    /* Outgoing Message Bubble (You) */
    .wa-bubble-me {
        background-color: #d9fdd3;
        color: #111b21;
        padding: 8px 12px;
        border-radius: 7.5px 0px 7.5px 7.5px;
        margin-bottom: 6px;
        max-width: 75%;
        float: right;
        clear: both;
        box-shadow: 0 1px 0.5px rgba(0,0,0,0.13);
        font-size: 0.95rem;
        word-wrap: break-word;
    }
    
    /* Incoming Message Bubble (Peer) */
    .wa-bubble-peer {
        background-color: #ffffff;
        color: #111b21;
        padding: 8px 12px;
        border-radius: 0px 7.5px 7.5px 7.5px;
        margin-bottom: 6px;
        max-width: 75%;
        float: left;
        clear: both;
        box-shadow: 0 1px 0.5px rgba(0,0,0,0.13);
        font-size: 0.95rem;
        word-wrap: break-word;
    }
    
    /* Message Meta Time & Ticks */
    .wa-meta {
        font-size: 0.65rem;
        color: #667781;
        float: right;
        margin-left: 8px;
        margin-top: 4px;
        line-height: 1rem;
    }
    
    .wa-sender {
        font-size: 0.75rem;
        font-weight: bold;
        color: #005c4b;
        margin-bottom: 2px;
    }
    </style>
""", unsafe_allow_html=True)

# Data paths for persistent storage
DATA_DIR = "bluetalk_data"
os.makedirs(DATA_DIR, exist_ok=True)
CONTACTS_FILE = os.path.join(DATA_DIR, "contacts.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")

def load_json(filepath, default):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except Exception:
            return default
    return default

def save_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

# Initialize Session State
if "contacts" not in st.session_state:
    st.session_state.contacts = load_json(CONTACTS_FILE, {
        "Android Peer 1": {"address": "11:22:33:44:55:66", "status": "Online (Bluetooth)"}
    })

if "history" not in st.session_state:
    st.session_state.history = load_json(HISTORY_FILE, {
        "Android Peer 1": [
            {"sender": "Android Peer 1", "type": "text", "content": "Hey! Connected via offline Bluetooth RFCOMM.", "time": "09:41 AM"}
        ]
    })

if "active_contact" not in st.session_state:
    st.session_state.active_contact = list(st.session_state.contacts.keys())[0]

if "connection_mode" not in st.session_state:
    st.session_state.connection_mode = "Simulation Mode (Demo)"

# Sidebar - WhatsApp Chat List & Settings
with st.sidebar:
    st.markdown("### 💬 BlueTalk WhatsApp")
    st.caption("Offline P2P Bluetooth Messenger")
    
    st.markdown("---")
    st.subheader("📶 Transport Mode")
    st.session_state.connection_mode = st.selectbox(
        "Connection Type",
        ["Simulation Mode (Demo)", "Native Android BT Service Bridge"],
        index=0
    )
    
    if "Simulation" in st.session_state.connection_mode:
        st.info("ℹ️ Simulation active: Messages echo locally for UI verification.")
    else:
        st.success("🔵 Bound to Android Bluetooth RFCOMM socket.")

    st.markdown("---")
    st.subheader("Chats")
    
    with st.expander("➕ New Peer Contact"):
        new_name = st.text_input("Contact Name")
        new_addr = st.text_input("Bluetooth MAC Address", placeholder="AA:BB:CC:DD:EE:FF")
        if st.button("Add Contact"):
            if new_name and new_addr:
                st.session_state.contacts[new_name] = {"address": new_addr, "status": "Paired"}
                if new_name not in st.session_state.history:
                    st.session_state.history[new_name] = []
                save_json(CONTACTS_FILE, st.session_state.contacts)
                st.success(f"Added {new_name}!")
                st.rerun()

    # Chat list items
    for contact in list(st.session_state.contacts.keys()):
        if st.button(f"👤 {contact}", use_container_width=True):
            st.session_state.active_contact = contact
            st.rerun()

    st.markdown("---")
    if st.button("🗑️ Clear Active Chat"):
        st.session_state.history[st.session_state.active_contact] = []
        save_json(HISTORY_FILE, st.session_state.history)
        st.rerun()

# Main WhatsApp Window Layout
active_peer = st.session_state.active_contact
peer_info = st.session_state.contacts.get(active_peer, {"address": "Unknown", "status": "Offline"})

# WhatsApp Header Bar
st.markdown(f"""
    <div class="wa-header">
        <div style="font-size: 1.5rem; margin-right: 12px;">👤</div>
        <div>
            <div style="font-weight: 600;">{active_peer}</div>
            <div style="font-size: 0.75rem; opacity: 0.85;">BT Address: {peer_info['address']} • {peer_info['status']}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Chat History Area
messages = st.session_state.history.get(active_peer, [])

st.markdown('<div class="wa-chat-container">', unsafe_allow_html=True)
for msg in messages:
    is_me = (msg["sender"] == "You")
    bubble_class = "wa-bubble-me" if is_me else "wa-bubble-peer"
    
    st.markdown(f'<div class="{bubble_class}">', unsafe_allow_html=True)
    if not is_me:
        st.markdown(f'<div class="wa-sender">{msg["sender"]}</div>', unsafe_allow_html=True)
        
    if msg["type"] == "text":
        st.write(msg["content"])
    elif msg["type"] == "emoji":
        st.markdown(f"<h2 style='margin:0; padding:0;'>{msg['content']}</h2>", unsafe_allow_html=True)
    elif msg["type"] == "image":
        try:
            img_bytes = base64.b64decode(msg["content"])
            st.image(io.BytesIO(img_bytes), width=220)
        except Exception:
            st.error("[Corrupted Image]")
    elif msg["type"] == "file":
        st.markdown(f"📎 **File:** `{msg['filename']}`")
        try:
            file_bytes = base64.b64decode(msg["content"])
            st.download_button(
                label=f"Download {msg['filename']}",
                data=file_bytes,
                file_name=msg["filename"],
                mime="application/octet-stream",
                key=f"dl_{msg['time']}_{os.urandom(3).hex()}"
            )
        except Exception:
            st.error("[Corrupted File]")
            
    ticks = "✓✓" if is_me else ""
    st.markdown(f'<div class="wa-meta">{msg["time"]} {ticks}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# WhatsApp Bottom Input Toolbar
st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

with st.form("wa_message_form", clear_on_submit=True):
    cols = st.columns([5, 1, 1])
    with cols[0]:
        text_input = st.text_input("Type a message", placeholder="Type a message...", label_visibility="collapsed")
    with cols[1]:
        emoji_choice = st.selectbox("Emoji", ["😀", "🔥", "👍", "❤️", "🎉", "🚀", "None"], label_visibility="collapsed")
    with cols[2]:
        send_btn = st.form_submit_button("Send ➔", use_container_width=True)

# Media sharing expander styled subtly
with st.expander("📎 Attach Media / Document"):
    uploaded_file = st.file_uploader("Select image or file to transmit via Bluetooth", type=["png", "jpg", "jpeg", "pdf", "txt", "zip"])
    if uploaded_file is not None:
        if st.button("Send Attachment"):
            file_bytes = uploaded_file.read()
            encoded_content = base64.b64encode(file_bytes).decode('utf-8')
            is_image = uploaded_file.type.startswith("image")
            msg_type = "image" if is_image else "file"
            
            timestamp = datetime.datetime.now().strftime("%I:%M %p")
            new_msg = {
                "sender": "You",
                "type": msg_type,
                "content": encoded_content,
                "filename": uploaded_file.name,
                "time": timestamp
            }
            
            st.session_state.history[active_peer].append(new_msg)
            save_json(HISTORY_FILE, st.session_state.history)
            st.success("Attachment dispatched successfully!")
            st.rerun()

# Form Submission Logic
if send_btn:
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    payload_items = []
    
    if text_input.strip():
        payload_items.append({"type": "text", "content": text_input})
    if emoji_choice != "None":
        payload_items.append({"type": "emoji", "content": emoji_choice})
        
    if not payload_items and text_input.strip() == "":
        payload_items.append({"type": "text", "content": emoji_choice if emoji_choice != "None" else "👍"})

    for item in payload_items:
        st.session_state.history[active_peer].append({
            "sender": "You",
            "type": item["type"],
            "content": item["content"],
            "time": current_time
        })
        
    save_json(HISTORY_FILE, st.session_state.history)

    if "Simulation" in st.session_state.connection_mode:
        # Echo response for testing UI
        st.session_state.history[active_peer].append({
            "sender": active_peer,
            "type": "text",
            "content": "Received via Bluetooth socket.",
            "time": datetime.datetime.now().strftime("%I:%M %p")
        })
        save_json(HISTORY_FILE, st.session_state.history)

    st.rerun()
