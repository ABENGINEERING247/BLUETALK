import os
import json
import base64
import datetime
import streamlit as st
from PIL import Image
import io

st.set_page_config(
    page_title="BlueTalk - Offline Bluetooth Messenger",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { background-color: #efeae2; }
    .stTextInput input { border-radius: 20px !important; }
    .chat-bubble-me {
        background-color: #d9fdd3;
        color: #111b21;
        padding: 10px 14px;
        border-radius: 8px 0px 8px 8px;
        margin-bottom: 8px;
        max-width: 75%;
        float: right;
        clear: both;
        box-shadow: 0 1px 0.5px rgba(0,0,0,0.13);
    }
    .chat-bubble-peer {
        background-color: #ffffff;
        color: #111b21;
        padding: 10px 14px;
        border-radius: 0px 8px 8px 8px;
        margin-bottom: 8px;
        max-width: 75%;
        float: left;
        clear: both;
        box-shadow: 0 1px 0.5px rgba(0,0,0,0.13);
    }
    .chat-time {
        font-size: 0.65rem;
        color: #667781;
        text-align: right;
        margin-top: 4px;
    }
    </style>
""", unsafe_allow_html=True)

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

if "contacts" not in st.session_state:
    st.session_state.contacts = load_json(CONTACTS_FILE, {
        "Peer Device 1": {"address": "11:22:33:44:55:66", "status": "Available offline"}
    })

if "history" not in st.session_state:
    st.session_state.history = load_json(HISTORY_FILE, {
        "Peer Device 1": [
            {"sender": "Peer Device 1", "type": "text", "content": "Hey! Welcome to BlueTalk offline messenger.", "time": "10:00 AM"}
        ]
    })

if "active_contact" not in st.session_state:
    st.session_state.active_contact = list(st.session_state.contacts.keys())[0]

if "connection_mode" not in st.session_state:
    st.session_state.connection_mode = "Simulation Mode (Demo)"

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
        st.info("⚠️ Simulation active: Messages echo locally for UI testing.")
    else:
        st.success("🔵 Ready for Android RFCOMM socket bridge.")

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

active_peer = st.session_state.active_contact
peer_info = st.session_state.contacts.get(active_peer, {"address": "Unknown", "status": "Offline"})

st.markdown(f"### 💬 Chat with **{active_peer}**")
st.caption(f"Hardware ID / BT Address: `{peer_info['address']}` • Status: {peer_info['status']}")
st.divider()

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
                st.image(io.BytesIO(img_bytes), width=250)
            except Exception:
                st.error("[Corrupted Image Stream]")
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

st.markdown("<br><br>", unsafe_allow_html=True)

with st.form("message_form", clear_on_submit=True):
    cols = st.columns([5, 1, 1])
    with cols[0]:
        text_input = st.text_input("Type a message...", placeholder="Type message...", label_visibility="collapsed")
    with cols[1]:
        emoji_choice = st.selectbox("Emoji", ["💬", "😀", "🔥", "👍", "❤️", "🎉", "🚀"], label_visibility="collapsed")
    with cols[2]:
        submit_btn = st.form_submit_button("Send ➔", use_container_width=True)

if submit_btn:
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    if text_input.strip():
        st.session_state.history[active_peer].append({
            "sender": "You", "type": "text", "content": text_input, "time": current_time
        })
    if emoji_choice != "💬":
        st.session_state.history[active_peer].append({
            "sender": "You", "type": "emoji", "content": emoji_choice, "time": current_time
        })
        
    save_json(HISTORY_FILE, st.session_state.history)

    if "Simulation" in st.session_state.connection_mode:
        st.session_state.history[active_peer].append({
            "sender": active_peer, "type": "text", "content": "Echo: Received message via Bluetooth loopback.", "time": current_time
        })
        save_json(HISTORY_FILE, st.session_state.history)
    st.rerun()
