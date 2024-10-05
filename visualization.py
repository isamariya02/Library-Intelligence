import streamlit as st
import mysql.connector
from mysql.connector import Error
import matplotlib.pyplot as plt
import pandas as pd

# Function to fetch thumbs up and thumbs down counts
def fetch_thumbs_counts():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            database="feedback_db",
            user="root",
            password="root@123"
        )
        if conn.is_connected():
            query = """
                SELECT
                    (SELECT COUNT(*) FROM thumbs_feedback WHERE thumbs_up > 0) AS thumbs_up_count,
                    (SELECT COUNT(*) FROM thumbs_feedback WHERE thumbs_down > 0) AS thumbs_down_count
            """
            df = pd.read_sql(query, conn)
            return df.iloc[0]
        else:
            st.error("Unable to connect to the feedback database.")
    except Error as e:
        st.error(f"Error: {e}")
    finally:
        if conn.is_connected():
            conn.close()

# Function to fetch overall ratings
def fetch_overall_ratings():
    conn = None
    try:
        conn = mysql.connector.connect(
            host="localhost",
            database="feedback_db",
            user="root",
            password="root@123"
        )
        if conn.is_connected():
            query = "SELECT overall_rating, COUNT(*) as count FROM feedback_1 GROUP BY overall_rating"
            df = pd.read_sql(query, conn)
            return df
        else:
            st.error("Unable to connect to the feedback database.")
    except Error as e:
        st.error(f"Error: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()

# Function to fetch thumbs up/thumbs down distribution by date
def fetch_thumbs_counts_by_date():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            database="feedback_db",
            user="root",
            password="root@123"
        )
        if conn.is_connected():
            query = """
                SELECT DATE(feedback_date) as date, 
                       SUM(thumbs_up) as thumbs_up_count,
                       SUM(thumbs_down) as thumbs_down_count
                FROM thumbs_feedback
                GROUP BY DATE(feedback_date)
                ORDER BY DATE(feedback_date)
            """
            df = pd.read_sql(query, conn)
            return df
        else:
            st.error("Unable to connect to the feedback database.")
    except Error as e:
        st.error(f"Error: {e}")
    finally:
        if conn.is_connected():
            conn.close()

# Function to fetch ratings trend over time
def fetch_ratings_trend():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            database="feedback_db",
            user="root",
            password="root@123"
        )
        if conn.is_connected():
            query = """
                SELECT DATE(feedback_date) as date, 
                       AVG(overall_rating) as average_rating
                FROM feedback_1
                GROUP BY DATE(feedback_date)
                ORDER BY DATE(feedback_date)
            """
            df = pd.read_sql(query, conn)
            return df
        else:
            st.error("Unable to connect to the feedback database.")
    except Error as e:
        st.error(f"Error: {e}")
    finally:
        if conn.is_connected():
            conn.close()

# Main function to display the plots
def show_plots():
    st.title("Feedback Analysis")

    # Set background color
    st.markdown("""
        <style>
            [data-testid="stAppViewContainer"] {
                background-color: #F1F5F9; /* Light gray background color */
            }
            [data-testid="stSidebar"] {
                background-color: #F1F5F9; /* Same background color as the page */
            }
            [data-testid="stBottom"] {
                background-color: #F1F5F9 !important;
                padding: 0;
            }
            [data-testid="stBottom"] .st-emotion-cache-1uj96rm {
                background-color: #F1F5F9 !important;
            }
            [data-testid="stBottom"] .st-emotion-cache-uhkwx6 {
                background-color: #F1F5F9 !important;
            }
            [data-testid="stChatInput"] {
                background-color: #FFFFFF !important;
                border: 2px solid #EEEEFA;
                border-radius: 16px;
            }
            [data-testid="stChatInput"]:focus {
                outline: none;
            }
            body, html {
                height: 100%;
                margin: 0;
            }
        </style>
    """, unsafe_allow_html=True)

    # Fetch and plot thumbs up/thumbs down counts
    thumbs_counts = fetch_thumbs_counts()
    if thumbs_counts is not None:
        st.subheader("Thumbs Up / Thumbs Down Counts")
        thumbs_up_count = thumbs_counts['thumbs_up_count']
        thumbs_down_count = thumbs_counts['thumbs_down_count']
        
        col1, col2 = st.columns(2)

        with col1:
            fig, ax = plt.subplots(figsize=(5, 6))  # Reduce figure size
            ax.bar(["Thumbs Up", "Thumbs Down"], [thumbs_up_count, thumbs_down_count], color=["blue", "grey"])
            ax.set_ylabel("Count")
            ax.set_title("Thumbs Up vs Thumbs Down")
            st.pyplot(fig)

        # Fetch and plot overall ratings
        overall_ratings_df = fetch_overall_ratings()
        if overall_ratings_df is not None:
            with col2:
                fig, ax = plt.subplots(figsize=(5, 3))  # Reduce figure size
                ax.pie(
                    overall_ratings_df['count'],
                    labels=overall_ratings_df['overall_rating'].astype(str),
                    autopct='%1.1f%%',
                    startangle=140,
                    colors=plt.cm.Paired(range(len(overall_ratings_df)))
                )
                ax.set_title("Overall Ratings Distribution")
                st.pyplot(fig)

    # Fetch and plot thumbs up/thumbs down distribution by date
    thumbs_counts_by_date = fetch_thumbs_counts_by_date()
    if thumbs_counts_by_date is not None:
        st.subheader("Thumbs Up / Thumbs Down Distribution Over Time")
        col1, col2 = st.columns(2)

        with col1:
            fig, ax = plt.subplots(figsize=(5, 3))  # Reduce figure size
            ax.plot(thumbs_counts_by_date['date'], thumbs_counts_by_date['thumbs_up_count'], label='Thumbs Up', color='green', marker='o')
            ax.set_xlabel("Date")
            ax.set_ylabel("Count")
            ax.set_title("Thumbs Up Distribution Over Time")
            plt.xticks(rotation=45)
            st.pyplot(fig)

        with col2:
            fig, ax = plt.subplots(figsize=(5, 3))  # Reduce figure size
            ax.plot(thumbs_counts_by_date['date'], thumbs_counts_by_date['thumbs_down_count'], label='Thumbs Down', color='red', marker='o')
            ax.set_xlabel("Date")
            ax.set_ylabel("Count")
            ax.set_title("Thumbs Down Distribution Over Time")
            plt.xticks(rotation=45)
            st.pyplot(fig)

    # Fetch and plot ratings trend over time
    ratings_trend = fetch_ratings_trend()
    if ratings_trend is not None:
        st.subheader("Ratings Trend Over Time")
        fig, ax = plt.subplots(figsize=(10, 4))  # Adjust figure size for better visibility
        ax.plot(ratings_trend['date'], ratings_trend['average_rating'], color='blue', marker='o')
        ax.set_xlabel("Date")
        ax.set_ylabel("Average Rating")
        ax.set_title("Ratings Trend Over Time")
        plt.xticks(rotation=45)
        st.pyplot(fig)

# --- MAIN APPLICATION ---

st.set_page_config(page_title="Feedback Analysis", page_icon=":bar_chart:")

# Display the plots
show_plots()
