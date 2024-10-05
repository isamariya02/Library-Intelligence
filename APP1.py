import streamlit as st
from chat_with_docs import configure_retrieval_chain
from langchain_community.callbacks.streamlit.streamlit_callback_handler import StreamlitCallbackHandler
import requests
import mysql.connector
from mysql.connector import Error

# Set Streamlit page configuration
st.set_page_config(page_title="Library Intelligence for Christ University", layout="wide")  # Set layout to wide for more space

# Function to read HTML file
def read_html(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Initialize session state for navigation
if "chat_started" not in st.session_state:
    st.session_state.chat_started = False

# Initialize chat history if it does not exist
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Initialize session state for feedback form visibility
if "show_feedback_form" not in st.session_state:
    st.session_state.show_feedback_form = False

# Display home page or chat UI based on session state
if not st.session_state.chat_started:
    if st.query_params.get("start_chat"):
        st.session_state.chat_started = True
        st.rerun()
    else:
        home_page_html = read_html("./homepage.html")
        st.markdown(home_page_html, unsafe_allow_html=True)
else:
    # Configure the conversational retrieval chain with the permanent document
    CONV_CHAIN = configure_retrieval_chain()

    # Display the heading and boxes if show_elements is True
    if "show_elements" not in st.session_state:
        st.session_state.show_elements = True

    if st.session_state.show_elements:
        title_html = """
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap');
                .gradient-title {
                    font-family:Inter;
                    font-size: 48px;
                    font-weight:500;
                    font-style:normal;
                    text-align: left;
                    margin: 0;
                }
                .gradient-text {
                    background: linear-gradient(45deg,#27337B,#6A7FFD); /* Gradient colors */
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }
                .plain-text {
                    color: var(--Nightingale-Gray-50, #64748B); /* Color for the plain text */
                }
            </style>
            <h1 class="gradient-title">
                <span class="plain-text">Hello </span><span class="gradient-text">Christite!</span><span class="plain-text"><br>What would you like to read?</br></span>
            </h1>
        """
        background_color = """
    <style>
        /* Apply background color to the entire app view container */
        [data-testid="stAppViewContainer"] {
            background-color: #F1F5F9; /* Light gray background color */
        }
        
        /* Apply background color to the sidebar */
        [data-testid="stSidebar"] {
            background-color: #F1F5F9; /* Same background color as the page */
        }

        /* Apply background color to the footer and its inner containers */
        [data-testid="stBottom"] {
            background-color: #F1F5F9 !important; /* Force the background color */
            padding: 0; /* Adjust padding as needed */
        }
        
        /* Apply background color to inner containers of the footer */
        [data-testid="stBottom"] .st-emotion-cache-1uj96rm {
            background-color: #F1F5F9 !important;
        }
        
        [data-testid="stBottom"] .st-emotion-cache-uhkwx6 {
            background-color: #F1F5F9 !important;
        }
        
        /* Apply background color to the chat input area */
        [data-testid="stChatInput"] {
            background-color: #FFFFFF !important;  
        }
        [data-testid="stChatInput"] {
            border: 2px solid #EEEEFA;
            border-radius: 16px;
            background-color: #FFFFFF; /* Set a background color for the input */
        }

        /* Remove the default focus border */
        [data-testid="stChatInput"]:focus {
            outline: none;
        }
        
        /* Ensure the body takes full height */
        body, html {
            height: 100%;
            margin: 0;
        }
    </style>
"""
        st.markdown(background_color, unsafe_allow_html=True)
        st.markdown(title_html, unsafe_allow_html=True)
        box_css = """
            <style>
                .box-container {
                    display: flex;
                    margin-top:-12px;
                }

                .box {
                    border: 2px solid #6A7FFD;
                    border-radius: 12px; 
                    border: 1px solid #E2E8F0;
                    background-color: #FFFFFF; 
                    padding: 12px 16px;
                    width:25%;
                    height:120px;
                    margin: 8px; 
                    display: flex;
                    align-items: flex-start;
                    align-self: stretch;
                    font-size:12px;
                }
                
                .box:hover {
                    background-color: #FFFFFF; /* Ensure hover state matches default */
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1); /* Ensure hover state matches default */
                }
            </style>
        """
        st.markdown(box_css, unsafe_allow_html=True)
        st.markdown('<div class="box-container">'
                    '<div class="box">What research publication houses does the library have? Also, Do you have digital access to IEEE publications?</div>'
                    '<div class="box">Are there any books by J.K. Rowling available?</div>'
                    '<div class="box">Suggest some beginner friendly books for an aspiring data scientist</div>'
                    '<div class="box">What are the library hours?</div>'
                    '</div>', unsafe_allow_html=True)

    # Display previous chat messages
    if st.session_state.chat_history:
        for role, message in st.session_state.chat_history:
            st.chat_message(role).write(message)

    # Handle new user input
    user_query = st.chat_input(placeholder="Type your query/message here!", key="user_input")

    if user_query:
        # Set session state to hide elements
        st.session_state.show_elements = False

        # Add user query to chat history
        st.session_state.chat_history.append(("user", user_query))

        # Add user query to chat messages
        st.chat_message("user").write(user_query)

        container = st.empty()
        stream_handler = StreamlitCallbackHandler(container)

        # Prepare the input data with both question and chat history
        input_data = {"question": user_query, "chat_history": st.session_state.chat_history}

        with st.chat_message("assistant"):
            response = CONV_CHAIN.run(input_data, callbacks=[stream_handler])

            # Display the response from the chatbot
            if response:
                container.markdown(response)

                # Update chat history with the response
                st.session_state.chat_history.append(("assistant", response))

    # Handle book request button
    if "show_book_request_form" in st.session_state and st.session_state.show_book_request_form:
        st.markdown(read_html("book_request.html"), unsafe_allow_html=True)

        # Handling form submission
        with st.form(key='book_request_form'):
            student_name = st.text_input("Student Name")
            department = st.text_input("Department")
            book_title = st.text_input("Book Title")
            book_author = st.text_input("Book Author")
            submit_button = st.form_submit_button(label='Submit')

            if submit_button:
                response = requests.post("http://localhost:5000/submit_request", json={
                    'studentName': student_name,
                    'department': department,
                    'bookTitle': book_title,
                    'bookAuthor': book_author
                })
                if response.ok:
                    st.success("Your request has been sent successfully.")
                else:
                    st.error("There was an error sending your request.")

# Sidebar for feedback form
st.sidebar.title("Feedback")

# Feedback button
if st.sidebar.button("Submit Feedback", key="feedback_button"):
    st.session_state.show_feedback_form = True

# Display feedback form in the sidebar
if st.session_state.show_feedback_form:
    st.sidebar.subheader("We value your feedback")
    
    # Feedback options: Thumbs Up/Down
    feedback_type = st.sidebar.radio("Please provide your feedback:", ["Thumbs Up", "Thumbs Down"], index=0, key="feedback_type")
    
    # Overall rating
    rating = st.sidebar.selectbox("Rate your overall experience (1 to 5):", [1, 2, 3, 4, 5], index=2, key="overall_rating")
    
    # Optional comments
    comments = st.sidebar.text_area("Any additional comments (optional):", key="comments")
    
    # Submit feedback button
    feedback_submit = st.sidebar.button(label='Submit Feedback', key="submit_feedback")

    if feedback_submit:
        try:
            # Connect to MySQL database
            conn = mysql.connector.connect(
                host="localhost",
                database="feedback_db",  # Change to your database name
                user="root",
                password="root@123"
            )
            
            if conn.is_connected():
                cursor = conn.cursor()
                
                # Insert feedback into the appropriate table
                if feedback_type == "Thumbs Up":
                    query = "INSERT INTO thumbs_feedback (thumbs_up) VALUES (1)"
                else:
                    query = "INSERT INTO thumbs_feedback (thumbs_down) VALUES (1)"
                
                cursor.execute(query)
                conn.commit()

                # Optionally insert into feedback_1 table for detailed feedback
                detailed_feedback_query = "INSERT INTO feedback_1 (overall_rating, comments) VALUES (%s, %s)"
                cursor.execute(detailed_feedback_query, (rating, comments))
                conn.commit()
                
                st.sidebar.success("Thank you for your feedback!")
                st.session_state.show_feedback_form = False  # Hide the form after submission
                
        except Error as e:
            st.sidebar.error(f"Error while connecting to MySQL: {e}")
            
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
