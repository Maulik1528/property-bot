import streamlit as st
from streamlit_chat import message
from ollama_call import OllamaChat
from language_detect import LanguageDetector
from information_extract import InformationExtractor
from web_scraper import WebScraper
from csv_scraper import CSVScraper  # Import the CSVScraper class

st.header("Chat with Bot – Your Property Partner")

# Sidebar Configuration
st.sidebar.title("Configuration")
communication_language = st.sidebar.selectbox("Communication Language", ["English", "Spanish", "French", "Detect"])

# Display detected language in the sidebar if available
if "language_detected" in st.session_state:
    st.sidebar.text(f"Detected Language: {st.session_state['language_detected']}")

# Check if user_type has changed
if "user_type" not in st.session_state:
    st.session_state["user_type"] = "Buyer"  # Default value

user_type = st.sidebar.selectbox("User Type", ["Buyer", "Seller", "Tenant", "Landlord"], index=["Buyer", "Seller", "Tenant", "Landlord"].index(st.session_state["user_type"]))

# Option to upload a document or paste a web link
upload_option = st.sidebar.radio("Options", ["Chat", "Upload Document", "Paste Web Link"], index=0)

# If upload option is selected, switch to upload document or web link window
if upload_option in ["Upload Document", "Paste Web Link"]:
    st.session_state["upload_mode"] = True
else:
    st.session_state["upload_mode"] = False

# If user_type has changed, clear chat history and reload the page
if user_type != st.session_state["user_type"]:
    st.session_state["user_type"] = user_type
    st.session_state["chat_history"] = [("bot", "Hello! I'm here to assist you with your property needs.")]
    st.rerun()

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [("bot", "Hello! I'm here to assist you with your property needs.")]

# Initialize OllamaChat
ollama_chat = OllamaChat()

# Initialize LanguageDetector
language_detector = LanguageDetector()

# Initialize InformationExtractor
information_extractor = InformationExtractor(ollama_chat)

# Function to handle sending message
def send_message():
    user_input = st.session_state["input"].strip()

    if user_input:
        # Detect language if communication_language is set to Detect and it's the first input
        if communication_language == "Detect" and "language_detected" not in st.session_state:
            detected_language = language_detector.detect_language(user_input)
            st.session_state["language_detected"] = detected_language

        # Determine the language for generating questions
        question_language = st.session_state.get("language_detected", communication_language)

        # Append user message
        st.session_state["chat_history"].append(("user", user_input))

        # Define a dictionary for user types and their required details
        user_details = {
            "Buyer": ["name", "property_type", "budget", "preferred_location"],
            "Seller": ["property_type", "location", "selling_price"],
            "Tenant": ["property_type", "budget", "move_in_date"],
            "Landlord": ["availability", "rental_status", "furnishing_details"]
        }

        # Define a dictionary for user types and their responses
        user_responses = {
            "Buyer": "As a buyer, I can assist you in finding properties.",
            "Seller": "As a seller, I can assist you in listing your property.",
            "Tenant": "As a tenant, I can help you find rental properties.",
            "Landlord": "As a landlord, I can assist you in managing your rental properties."
        }

        # Process user input based on user type
        for detail in user_details.get(user_type, []):
            if detail not in st.session_state:
                question = ollama_chat.get_ai_response([
                    {"role": "system", "content": f"Generate a single and concise question to ask user for {detail} in {question_language}. Only return the question."},
                    {"role": "user", "content": f"Generate question for {detail}."}
                ])
                st.session_state["chat_history"].append(("bot", question))
                st.session_state[detail] = user_input
                break
        else:
            bot_response = f"Bot: {user_responses.get(user_type, 'I am here to help with your property needs.')} You asked: {user_input}"
            st.session_state["chat_history"].append(("bot", bot_response))

        # Clear the input field
        st.session_state["input"] = ""

# Display chat, upload document, or paste web link window based on the selected option
if st.session_state.get("upload_mode", False):
    if upload_option == "Upload Document":
        st.subheader("Upload Document")
        uploaded_file = st.file_uploader("Choose a file")
        if uploaded_file is not None:
            st.success("File uploaded successfully!")
            metadata = st.selectbox("Select metadata for the document", ["Buyer", "Seller", "Tenant", "Landlord"])
            if metadata:  # Ensure metadata is selected
                if st.button("Store Document"):
                    csv_scraper = CSVScraper(uploaded_file)
                    csv_scraper.run()
                    st.success("Document processed and stored successfully!")
    elif upload_option == "Paste Web Link":
        st.subheader("Paste Web Link")
        web_link = st.text_input("Enter the web link")
        if web_link:
            st.success("Web link entered successfully!")
            if st.button("Store Data"):
                scraper = WebScraper(web_link)
                scraper.run()
                st.success("Web data scraped and stored successfully!")
else:
    # Scrollable Chat Message Container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for index, (role, text) in enumerate(st.session_state["chat_history"]):
        message(text, is_user=(role == "user"), key=f"{index}_{role}", allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Fixed Input Box at Bottom
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    col1, col2 = st.columns([8, 1])

    with col1:
        st.text_input("", key="input", placeholder="Type your message...", label_visibility="collapsed")

    with col2:
        st.button("➤", key="send", help="Send Message", use_container_width=True, on_click=send_message)