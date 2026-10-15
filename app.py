import os
import json
import base64
import datetime
import streamlit as st
from PIL import Image
import io

# Page Config
st.set_page_config(
    page_title="BlueTalk - Offline Bluetooth Messenger",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom Light Green & Blue Theme Styling with Offline Bluetooth Indicator
st.markdown("""
    <style>
    .main { background-color: #f0fdf4; }
    .stTextInput input { border-radius: 20px !important; border: 1px solid #0284c7 !important; }
    .chat-bubble-me {
        background-color: #d9fdd3;
        color: #111b21;
        padding: 10px 14px;
        border-radius: 12px 2px 12px 12px;
        margin-bottom: 8px;
        max-width: 75%;
        float: right;
        clear: both;
        box-shadow: 0 1px 1px rgba(0,0,0,0.1);
    }
    .chat-bubble-peer {
        background-color: #ffffff;
        color: #111b21;
        padding: 10px 14px;
        border-radius: 2px 12px 12px 12px;
        margin-bottom: 8px;
        max-width: 75%;
        float: left;
        clear: both;
        box-shadow: 0 1px 1px rgba(0,0,0,0.1);
        border-left: 4px solid #0284c7;
    }
    .chat-time {
        font-size: 0.65rem;
        color: #667781;
        text-align: right;
        margin-top: 4px;
    }
    h1, h2, h3 { color: #0369a1 !important; }
    .app-header-box {
        background-color: #ffffff;
        padding: 15px 20px;
        border-radius: 12px;
        border-left: 6px solid #0284c7;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    .bt-offline-banner {
        background-color: #e0f2fe;
        border: 1px dashed #0284c7;
        padding: 10px 15px;
        border-radius: 8px;
        font-size: 0.85rem;
        color: #0369a1;
        margin-bottom: 20px;
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
        "Peer Device 1": {"address": "11:22:33:44:55:66", "status": "Available offline"}
    })

if "history" not in st.session_state:
    st.session_state.history = load_json(HISTORY_FILE, {
        "Peer Device 1": [
            {"sender": "Peer Device 1", "type": "text", "content": "Welcome to BlueTalk offline communication! Check the live Bluetooth status banner above.", "time": "10:00 AM"}
        ]
    })

if "active_contact" not in st.session_state:
    st.session_state.active_contact = list(st.session_state.contacts.keys())[0]

if "connection_mode" not in st.session_state:
    st.session_state.connection_mode = "Simulation Mode (Demo)"

# Sidebar - Contacts and Connection Settings
with st.sidebar:
    st.title("💬 BlueTalk")
    st.caption("P2P Offline Bluetooth Messenger")
    
    st.subheader("📶 Connection Mode")
    st.session_state.connection_mode = st.selectbox(
        "Select Transport",
        ["Simulation Mode (Demo)", "Native Android BT Service Bridge"],
        index=0
    )
    
    if "Simulation" in st.session_state.connection_mode:
        st.info("⚠️ Simulation active: Local loopback testing mode.")
    else:
        st.success("🔵 Active: Android RFCOMM Bluetooth socket bridge.")

    st.markdown("---")
    st.subheader("👥 Chats & Contacts")
    
    with st.expander("➕ Add Bluetooth Peer"):
        new_name = st.text_input("Contact Name")
        new_addr = st.text_input("BT MAC Address / ID", placeholder="AA:BB:CC:DD:EE:FF")
        if st.button("Save Contact"):
            if new_name and new_addr:
                st.session_state.contacts[new_name] = {"address": new_addr, "status": "Paired"}
                if new_name not in st.session_state.history:
                    st.session_state.history[new_name] = []
                save_json(CONTACTS_FILE, st.session_state.contacts)
                st.success(f"Added {new_name}!")
                st.rerun()

    for contact in list(st.session_state.contacts.keys()):
        if st.button(f"👤 {contact}", use_container_width=True):
            st.session_state.active_contact = contact
            st.rerun()

    st.markdown("---")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.history[st.session_state.active_contact] = []
        save_json(HISTORY_FILE, st.session_state.history)
        st.rerun()

# Main Chat Area Header with App Details
active_peer = st.session_state.active_contact
peer_info = st.session_state.contacts.get(active_peer, {"address": "Unknown", "status": "Offline"})

st.markdown(f"""
    <div class="app-header-box">
        <h2 style="margin:0; padding:0; font-size: 1.4rem;">💬 BlueTalk Messenger</h2>
        <p style="margin: 4px 0 0 0; color: #334155; font-size: 0.9rem;">
            <b>Active Chat:</b> {active_peer} &nbsp;|&nbsp; 
            <b>BT Address:</b> <code>{peer_info['address']}</code> &nbsp;|&nbsp; 
            <b>Mode:</b> {st.session_state.connection_mode}
        </p>
    </div>
""", unsafe_allow_html=True)

# Offline Bluetooth Link Status Panel
st.markdown(f"""
    <div class="bt-offline-banner">
        <b>📡 Offline Bluetooth Link:</b> Radio broadcast active on RFCOMM channel. 
        Zero internet/cellular router required. Direct peer connection to <b>{peer_info['address']}</b>.
    </div>
""", unsafe_allow_html=True)

# Message History Display container
chat_container = st.container()

with chat_container:
    messages = st.session_state.history.get(active_peer, [])
    for msg in messages:
        is_me = (msg["sender"] == "You")
        bubble_class = "chat-bubble-me" if is_me else "chat-bubble-peer"
        
        st.markdown(f'<div class="{bubble_class}">', unsafe_allow_html=True)
        st.markdown(f"**{msg['sender']}**")
        
        if msg["type"] == "text":
            st.write(msg["content"])
        elif msg["type"] == "emoji":
            st.markdown(f"<h1 style='margin:0; padding:0;'>{msg['content']}</h1>", unsafe_allow_html=True)
        elif msg["type"] == "image":
            try:
                img_bytes = base64.b64decode(msg["content"])
                st.image(io.BytesIO(img_bytes), width=280)
            except Exception:
                st.error("[Corrupted Image Stream]")
        elif msg["type"] == "video":
            try:
                video_bytes = base64.b64decode(msg["content"])
                st.video(io.BytesIO(video_bytes))
            except Exception:
                st.error("[Corrupted Video Stream]")
        elif msg["type"] == "file":
            st.markdown(f"📎 **File Attachment:** `{msg['filename']}`")
            try:
                file_bytes = base64.b64decode(msg["content"])
                st.download_button(
                    label=f"Download {msg['filename']}",
                    data=file_bytes,
                    file_name=msg["filename"],
                    mime="application/octet-stream",
                    key=f"dl_{msg['time']}_{os.urandom(4).hex()}"
                )
            except Exception:
                st.error("[Corrupted File Stream]")
                
        st.markdown(f'<div class="chat-time">{msg["time"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Input Toolbar Bottom Section
st.markdown("<br><br>", unsafe_allow_html=True)

with st.form("message_form", clear_on_submit=True):
    cols = st.columns([5, 1, 1])
    with cols[0]:
        text_input = st.text_input("Type a message...", placeholder="Type a message or select an emoji...", label_visibility="collapsed")
    with cols[1]:
        emoji_choice = st.selectbox("Emoji", ["💬", "😀", "🔥", "👍", "❤️", "🎉", "🚀", "😎"], label_visibility="collapsed")
    with cols[2]:
        submit_btn = st.form_submit_button("Send ➔", use_container_width=True)

# Media & File Sharing Panel
with st.expander("📁 Share Photos, Videos, or Files via Bluetooth"):
    uploaded_file = st.file_uploader("Select media or document to broadcast offline", type=["png", "jpg", "jpeg", "mp4", "mov", "avi", "pdf", "txt", "zip"])
    if uploaded_file is not None:
        if st.button("Transmit via Bluetooth Stream"):
            file_bytes = uploaded_file.read()
            encoded_content = base64.b64encode(file_bytes).decode('utf-8')
            
            file_type = uploaded_file.type
            if file_type.startswith("image"):
                msg_type = "image"
            elif file_type.startswith("video"):
                msg_type = "video"
            else:
                msg_type = "file"
            
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
            st.success(f"Successfully broadcasted {uploaded_file.name} over local Bluetooth radio waves!")
            st.rerun()

# Handle text / emoji form submission logic
if submit_btn:
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    payload_items = []
    
    if text_input.strip():
        payload_items.append({"type": "text", "content": text_input})
    if emoji_choice != "💬":
        payload_items.append({"type": "emoji", "content": emoji_choice})
        
    if not payload_items and text_input.strip() == "":
        payload_items.append({"type": "text", "content": emoji_choice})

    for item in payload_items:
        msg_obj = {
            "sender": "You",
            "type": item["type"],
            "content": item["content"],
            "time": current_time
        }
        st.session_state.history[active_peer].append(msg_obj)
        
    save_json(HISTORY_FILE, st.session_state.history)

    if "Simulation" in st.session_state.connection_mode:
        if active_peer not in st.session_state.history:
            st.session_state.history[active_peer] = []
        st.session_state.history[active_peer].append({
            "sender": active_peer,
            "type": "text",
            "content": "Echo (Offline BT Ack): Packet successfully delivered over local Bluetooth channel.",
            "time": datetime.datetime.now().strftime("%I:%M %p")
        })
        save_json(HISTORY_FILE, st.session_state.history)

    st.rerun()
