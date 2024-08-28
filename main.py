import streamlit as st
import google.generativeai as genai
import json
import requests
import base64
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
genai.configure(api_key=API_KEY)

# Instantiate the generative model
model = genai.GenerativeModel('gemini-1.5-flash')
chat = model.start_chat()


st.set_page_config(
    page_title="Star Medical",
    page_icon="star.png",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "This is a medical chatbot integrated with Gemini AI."
    }
)

def format_address(address):
    parts = address.split(",")
    
    if len(parts) > 1:
        return ", ".join(parts[1:]).strip()
    return address


def initializeAI():
    #loading all .json files for reading each file has a different variable so the data is not overwritten
    with open('healthinfo.json', 'r') as file:
        data=json.load(file)

    data_str=json.dumps(data)
    with open('healthpro.json', 'r') as file:
        data2=json.load(file)

    data_str2=json.dumps(data2)
    with open('emergencynumbers.json', 'r') as file:
        data3=json.load(file)

    data_str3=json.dumps(data3)
    with open('testdef.json', 'r') as file:
        data4=json.load(file)

    data_str4=json.dumps(data4)
    with open('avgficcost.json', 'r') as file:
        data5=json.load(file)

    data_str5=json.dumps(data5)
    with open('symptoms.json', 'r') as file:
        data6=json.load(file)

    data_str6=json.dumps(data6)
    with open('healthtips.json', 'r') as file:
        data7=json.load(file)

    data_str7=json.dumps(data7)
    initialPrompt = """
    Your name is Star and you are a medical assistant chatbot. Your role is to be a helpful chatbot responding to the messages from a user. Here is the list of emergency center names and their corresponding contact numbers

    There are 3 public hospitals in St Lucia and 1 private one called Tapion Pierre Hospital. The other public ones are the Owen King European Union Hospital(OKEU Hospital), Victoria Hospital, St. Jude's Hospital, Soufreire Hospital and the Dennery Hospital.

    Give preliminary medical advice when given symptoms but always with the disclaimer
    that you are not a medical doctor and that you cannot provide a diagnosis.
    I also want you to keep this information so you can give it to users; 
    
    Your response should be a string in json format with two keys. A response
    key and a quit key. The value to the response key should be the response to
    the user's prompt and the value for the quit key should be the response if
    the user want to end the conversation. Here is an example of how I want your
    response to be to the prompt 'What is good morning in spanish?'. 
    {'response': 'Good morning in spanish is buenos dias', 'quit': false}
    """
    # Sending the message
    chat.send_message(initialPrompt)
    chat.send_message(data_str)
    chat.send_message(data_str2)
    chat.send_message(data_str3)
    chat.send_message(data_str4)
    chat.send_message(data_str5)
    chat.send_message(data_str6)
    chat.send_message(data_str7)

initializeAI()

st.title("Star - Medical Assistant Chatbot")
star_avatar = "⭐"
user_avatar="👤"

st.markdown(
    """
    <style>
    .main {
        background-color:#ADD8E6;
        background-size: cover;
        background-position: center;
    }
    
    div[data-testid="InputInstructions"] > span:nth-child(1) {
    visibility: hidden;
}
    </style>
    """,
    unsafe_allow_html=True
)


def get_location_info(location_name):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={location_name}&components=country:LC&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        
        # Check if results were returned
        if data['results']:
            location_info = data['results'][0]['formatted_address']
            lat = data['results'][0]['geometry']['location']['lat']
            lng = data['results'][0]['geometry']['location']['lng']
            maps_url = f"https://www.google.com/maps/?q={lat},{lng}"
            formatted_address = format_address(location_info)
            
            return f"Location found: {formatted_address}. [View on Google Maps]({maps_url})"
        else:
            return "Sorry, I couldn't find the location in Saint Lucia."
    else:
        return "There was an error retrieving the location."


if 'messages' not in st.session_state:
    st.session_state.messages = []
# Process input when the button is clicked or when the input field is submitted
def process_input():
    user_input = st.session_state.user_input

    if user_input:
        # Add user message to the conversation
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Check if the user input is a location-related query
        if "where" in user_input.lower() or "location" in user_input.lower() or "find" in user_input.lower():
            location_info = get_location_info(user_input)
            map = {"response": location_info, "quit": False}
        else:
            # Generate the response for non-location queries
            response = chat.send_message(user_input)
            reply = response.text

            # Extract the JSON response from the reply
            start = reply.find('{')
            end = reply.rfind('}') + 1
            map = json.loads(reply[start:end])
        quit_chat = map['quit']

        st.session_state.messages.append({"role": "assistant", "content": map['response']})

        st.session_state.user_input = ""

        if quit_chat:
            st.write("Exiting the chat. Goodbye!")
            st.stop()

# Display chat history
for message in st.session_state.messages:
    if message['role'] == 'user':
        with st.chat_message(name="You", avatar=user_avatar):
            st.write(message['content'])
    else:
        # Use st.chat_message for chatbot messages
        with st.chat_message(name="assistant", avatar=star_avatar):
            st.write(message['content'])

# Input field and button
user_input = st.text_input("Enter your message:", key='user_input', value="")
send_button = st.button("Send", on_click=process_input)