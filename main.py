import streamlit as st
import google.generativeai as genai
import os

# --- Configuration ---
# Set your page title and icon
st.set_page_config(
    page_title="Gemini Chatbot",
    page_icon="🤖",
    layout="centered"
)

# --- Sidebar: API Key Configuration ---
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter your Google Gemini API Key:", type="password")
    st.markdown("[Get your API Key here](https://aistudio.google.com/app/apikey)")
    
    # Optional: Model selection
    model_option = st.selectbox(
        "Choose a model:",
        ("gemini-2.5-flash")
    )

# --- Main App Logic ---
st.title("🤖 Gemini-Powered Chatbot")
st.caption("A chatbot powered by Google's Gemini AI and Streamlit")

# 1. Initialize Chat History in Session State
# This ensures the chat history persists even when the script reruns
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. Display Existing Chat History
# Iterate through the history and display messages using st.chat_message
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. Handle User Input
if prompt := st.chat_input("What would you like to ask?"):
    
    # Check if API Key is provided
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar to continue.")
        st.stop()

    # Configure the Gemini API
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_option)
    except Exception as e:
        st.error(f"Error configuring API: {e}")
        st.stop()

    # Display User Message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate Assistant Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Create a chat session with history (optional, for context)
            # Note: For simple implementation, we just send the history as context or use start_chat
            
            # Convert streamlit history to Gemini history format
            history = [
                {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
                for m in st.session_state.messages[:-1] # Exclude the latest user message which we will send now
            ]
            
            chat = model.start_chat(history=history)
            
            # Send message and stream response
            response = chat.send_message(prompt, stream=True)
            
            # Stream the response chunks
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
            full_response = "I'm sorry, I encountered an error."

    # Add assistant response to session state
    st.session_state.messages.append({"role": "assistant", "content": full_response})