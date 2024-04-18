# Job Applicants' Information Entry Web Application
# Developed by Hans Anthony T. Lim, BSCpE-4 @ La Salle University Ozamiz
# Developed for CHRMO Ozamiz

# Streamlit library for web app creation and gsheets connection
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Pandas library for data handling
import pandas as pd

# Time library for timings
import time

# base64 import for file download
import base64

# Libraries used for birth date
import datetime
import re

# Import Plotly for visualization
import plotly.express as px

# Import random for random number generator
import random

# Set page configurations here
st.set_page_config(
    page_title="CHRMO-AMS",
    page_icon=":black_nib:",
)

# Update google sheet function
def update_google_sheet(conn, data):
    conn.update(worksheet="Applicants", data=data)

# Update google sheet function for feedback
def update_feedback_google_sheet(conn, data):
    conn.update(worksheet="feedback", data=data)

# Function to refresh connection with google sheets in case of connection issues
def refresh():
    conn = st.connection("gsheets", type=GSheetsConnection, ttl=5)
    if conn is None:
        st.error("Failed to establish Google Sheets connection.")
    else:
        st.success("Google Sheets connection refreshed successfully.")
        time.sleep(1)
        st.rerun()

# Main function to determine if user is authenticated or not
def main():
    if "user" not in st.session_state:
        show_login_page()
    else:
        show_main_page()

# Login page
def show_login_page():
    st.sidebar.image('chrmo.png')
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    login_button = st.sidebar.button(label="Log in", type='primary')
    if login_button:
        if authenticate(username, password):
            st.session_state["user"] = username
            st.sidebar.success("Successfully logged in.")
            time.sleep(2)
            st.rerun()
        elif not all ([username, password]):
            st.sidebar.error("Enter a username or password.")
        else:

            st.sidebar.warning("Please check your credentials and try again.")
    st.sidebar.divider()

    st.image('chrmo2.png')

    # Web application description expander
    about_button = st.sidebar.button(label="About this app", type ='secondary')
    if about_button:
        st.sidebar.markdown('~ This web application is the CHRMO Applicant Management System (CHRMOAMS).')
        st.sidebar.markdown('~ This web application is used to manage various information of job applicants in the CHRMO.')
        st.sidebar.markdown('~ Developed for CHRMO Ozamiz')
        st.sidebar.markdown('~ Developed by Hans Anthony T. Lim, BS Computer Engineering 4 @ La Salle University Ozamiz.')
        if st.sidebar.button("Hide Description"):
            st.rerun()


def authenticate(username, password):
    user1_username = st.secrets["user1_username"]
    user1_password = st.secrets["user1_password"]

    if username == user1_username and password == user1_password:
        return True

    user2_username = st.secrets["user2_username"]
    user2_password = st.secrets["user2_password"]
    if username == user2_username and password == user2_password:
        return True

    user3_username = st.secrets["user3_username"]
    user3_password = st.secrets["user3_password"]
    if username == user3_username and password == user3_password:
        return True

    return False

# Gather the last 10 entries in the google sheet
def fetch_last_ten_entries(conn, filter_option="All"):
    existing_data = fetch_existing_data(conn)
    
    if filter_option == "Walk-in":
        last_ten_entries = existing_data[~existing_data["DATE"].str.contains("ONLINE")].tail(10)
    elif filter_option == "Online":
        last_ten_entries = existing_data[existing_data["DATE"].str.contains("ONLINE")].tail(10)
    else:
        last_ten_entries = existing_data.tail(10)
    
    # Replace commas in the "CONTACT NUMBER" column
    last_ten_entries = last_ten_entries.copy()
    last_ten_entries.loc[:, "CONTACT NUMBER"] = last_ten_entries["CONTACT NUMBER"].astype(str).str.replace(',', '')
    
    return last_ten_entries
    
# Show history function
def show_history_page():
    st.title("History (Last Ten Entries)")
    conn = st.connection("gsheets", type=GSheetsConnection, ttl=5)
    if conn is None:
        st.error("Failed to establish Google Sheets connection.")
        return

    filter_option = st.radio("Filter:", ("All", "Walk-in", "Online"), index=0)
    last_ten_entries = fetch_last_ten_entries(conn, filter_option)
    
    if st.button("Refresh"):
        st.rerun()
    st.write(last_ten_entries)
        
# Fetch existing data
def fetch_existing_data(conn):
    # Define the column names to retrieve from Google Sheets
    columns = ["DATE", "DATE SUBMITTED", "NAME", "CONTACT NUMBER", "DESIRED POSITION", 
               "FORWARDED FROM", "ADDRESS", "EDUCATIONAL ATTAINMENT", "CSC ELIGIBILITY", 
               "AGE", "GENDER", "CURRENT POSITION"]

    # Fetch data from Google Sheets with specified columns
    existing_data = conn.read(worksheet="Applicants", usecols=columns, ttl=5)
    
    # Drop any rows with all NaN values
    existing_data = existing_data.dropna(how="all")
    
    return existing_data

# Function to calculate age from birthday
def calculate_age(birthday):
    today = datetime.date.today()
    age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
    return age

# Function to parse date from mm/dd/yyyy string
def parse_date(date_str):
    try:
        match = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', date_str)
        if match:
            month = int(match.group(1))
            day = int(match.group(2))
            year = int(match.group(3))
            return datetime.date(year, month, day)
        else:
            return None
    except ValueError:
        return None

                        
# Arrage the new data into a dataframe
def create_applicant_dataframe(date, date_submitted, name, contact_number, desired_position, forwarded_from,
                               address, educational_attainment, csc_eligibility, birthday_or_age, gender, current_pos, online_submission):
    # Determine if the input is a valid date string in the format "MM/DD/YYYY"
    birthday = parse_date(birthday_or_age)
    if birthday:  # If it's a valid date string, calculate age
        age = calculate_age(birthday)
    else:  # Otherwise, assume it's an age
        try:
            age = int(birthday_or_age)
        except ValueError:
            age = None
    date_text = f"{date.strftime('%m/%d/%Y')}"
    if online_submission:  # Check if online submission or not
        date_text += "\n(ONLINE)"  # Add online indicator below the date in the entry
    
    # Get the data from the text field and  convert it to a list to add to the data frame
    applicant_data = {
        "DATE": [date_text],
        "DATE SUBMITTED": [date_submitted.strftime("%m/%d/%Y")],
        "NAME": [name],
        "CONTACT NUMBER": [contact_number],
        "DESIRED POSITION": [desired_position],
        "FORWARDED FROM": [forwarded_from],
        "ADDRESS": [address],
        "EDUCATIONAL ATTAINMENT": [educational_attainment],
        "CSC ELIGIBILITY": [csc_eligibility],
        "AGE": [age],
        "GENDER": [gender],
        "CURRENT POSITION": [current_pos]
    }
    return pd.DataFrame(applicant_data)

# Function to create a chart based on the number of applicants over time
def show_applicants_chart(existing_data):
    # Convert the 'DATE' column to datetime format
    existing_data['DATE'] = pd.to_datetime(existing_data['DATE'], errors='coerce')
    
    # Remove any rows with missing dates
    existing_data.dropna(subset=['DATE'], inplace=True)
    
    # Group the data by date and count the number of applicants for each date
    applicants_count = existing_data.groupby('DATE').size().reset_index(name='Applicants')
    st.title("Number of Applicants Over Time")
    # Create a line chart using Plotly
    fig = px.line(applicants_count, x='DATE', y='Applicants')
    fig.update_xaxes(title='Date')
    fig.update_yaxes(title='Number of Applicants')
    
    # Show the chart
    st.plotly_chart(fig)

def edit_data():
    st.title("Edit Existing Data")
    conn = st.connection("gsheets", type=GSheetsConnection, ttl=5)
    if conn is None:
        st.error("Failed to establish Google Sheets connection.")
        return

    existing_data = fetch_existing_data(conn)
    if not existing_data.empty:
        existing_data = existing_data.copy()
        existing_data.loc[:, "CONTACT NUMBER"] = existing_data["CONTACT NUMBER"].astype(str).str.replace(',', '')
        st.write("Enter full screen at the top right of the table")

        # Allow editing of all data directly
        edited_data = st.data_editor(existing_data)

        save_button = st.button(label="Save and Update", help="Save changes and update data.",type='primary')
        if save_button:
            # Update the original dataset with the edited data
            update_google_sheet(conn, edited_data)
            st.success("Data updated successfully!")
            time.sleep(3)
            st.rerun()

    else:
        st.info("No entries found.")
    

# Main Content
def main_content():
   
    st.title("Applicant Management System")
    st.write(f"👋 Welcome, {st.session_state['user']}. 👋")
    # Logout button
    logout_button = st.button(label="Log out", type='primary')
    if logout_button:
        st.write("Logging Out...")
        del st.session_state["user"]
        time.sleep(1)
        st.rerun()
    conn = st.connection("gsheets", type=GSheetsConnection, ttl=5)  # Connect to google sheets
    existing_data = fetch_existing_data(conn)  # Initially get all of the current data from the sheet
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["✍️ Enter New Applicant","🔎 Search","📑 History","📈 Analytics","💬 Feedback","✏️ Edit Data", "🛠️ Utilities"])
   # Enter Applicant Tab
    with tab1:
        # Display form for entering new applicant information
        with st.form(key="Applicants", clear_on_submit=True, border=True):
            st.markdown('**Fields marked with ( * ) are Required.**')
            st.markdown('Please use Caps Lock when entering info.')
            st.divider()
            # Ask the user if the submission is online or not
            online_submission = st.checkbox("Online Submission")
            
            # Divide the form into two columns
            col1, col2 = st.columns(2) 
        
            with col1: # Left column
                date = st.date_input(label="Date*", help="Select Date.", format="MM/DD/YYYY")
                name = st.text_input(label="Name of Applicant*", help="Full Name")
                desired_position = st.text_input(label="Desired Position", help="'ANY VACANT POSITION' if not provided.", autocomplete="ANY VACANT POSITION")
                address = st.text_input(label="Address")
                birthday_or_age = st.text_input(label="Date of Birth or Age", help="Enter Birthday in MM/DD/YYYY format or Age directly", placeholder="Enter date of birth (mm/dd/yyy) or age")
                gender = st.selectbox(label="Gender", options=["MALE", "FEMALE", "OTHER"], index=None, placeholder="Select Gender")
                current_pos = st.text_input(label="Current Position", help="leave blank if N/A")
            
            with col2: # Right column
                date_submitted = st.date_input(label="Date Submitted*", help="Select Date Submitted", value=None, format="MM/DD/YYYY")
                contact_number = st.text_input(label="Contact Number", help="Numeric only", max_chars=11)
                forwarded_from = st.text_input(label="Forwarded From", help="CHRMO", autocomplete = "CHRMO")
                educational_attainment = st.text_area(label="Educational Attainment")
                csc_eligibility = st.text_area(label="CSC Eligibility", help="Leave blank if N/A")

            
            st.divider()
            # Submit data button    
            submit_button = st.form_submit_button(label="Submit Data", type="primary")
            if submit_button:
                if not all([date, date_submitted, name]):  # Check required fields
                    st.error("Please fill in all required fields.")
                else:
                    # Prepare the dataframe to send to google sheets
                    new_applicant_df = create_applicant_dataframe(date, date_submitted, name, contact_number,
                                                                desired_position, forwarded_from, address,
                                                                educational_attainment, csc_eligibility,
                                                                birthday_or_age, gender, current_pos, online_submission)
                    # Append the data to the google sheet
                    updated_df = pd.concat([existing_data, new_applicant_df], ignore_index=True)
                    update_google_sheet(conn, updated_df)
                    st.success("Data Successfully Submitted.")


    # Search 
    with tab2:
        searchtype = st.selectbox("Search by:",("Name","Date","Date Submitted","Year"), index=None)  # Search filters
        if searchtype == "Name":
            search_name = st.text_input("Enter name (press 'enter' to search)", key="name_input")
            if search_name:
                search_results_name = existing_data[existing_data["NAME"].str.contains(search_name, case=False, na=False)]
                if not search_results_name.empty:
                    # Create a copy of the DataFrame before modifying it
                    search_results_name = search_results_name.copy()
                    search_results_name.loc[:, "CONTACT NUMBER"] = search_results_name["CONTACT NUMBER"].astype(str).str.replace(',', '')
                    st.subheader(f"Search Results for '{search_name}'")
                    st.write(search_results_name)
                else:
                    st.info(f"No results found for '{search_name}'")
        
        if searchtype == "Date":  # Search by Date
            search_date = st.date_input("Select a date", key="date_input")
            if search_date:
                filter_options = st.radio("Filter:", ("All", "Walk-in", "Online"), index=0, key="datefilter")
                if filter_options == "All":
                    search_results_date = existing_data[existing_data["DATE"].str.contains(search_date.strftime('%m/%d/%Y'), case=False, na=False)]
                elif filter_options == "Walk-in":
                    search_results_date = existing_data[(existing_data["DATE"].str.contains(search_date.strftime('%m/%d/%Y'), case=False, na=False)) & (~existing_data["DATE"].str.contains("ONLINE"))]
                else:
                    search_results_date = existing_data[(existing_data["DATE"].str.contains(search_date.strftime('%m/%d/%Y'), case=False, na=False)) & (existing_data["DATE"].str.contains("ONLINE"))]
                
                if not search_results_date.empty:
                    # Create a copy of the DataFrame before modifying it
                    search_results_date = search_results_date.copy()
                    # Remove the last two columns
                    search_results_date = search_results_date.iloc[:, :-3]
                    # Add a new column for REMARKS with default value
                    search_results_date["REMARKS"] = ""
                    # Convert 'CONTACT NUMBER' column to string and then replace commas
                    search_results_date.loc[:, "CONTACT NUMBER"] = search_results_date["CONTACT NUMBER"].astype(str).str.replace(',', '')
                    # Add a new column for row numbering
                    search_results_date.insert(0, ' ', range(1, len(search_results_date) + 1))
                    st.subheader(f"Search Results for '{search_date.strftime('%m/%d/%Y')}'")
                    st.write(search_results_date)

                    # Download button
                    csv = search_results_date.to_csv(index=False)
                    b64 = base64.b64encode(csv.encode()).decode()
                    file_name = f"{search_date.strftime('%m-%d-%Y')}.csv"
                    href = f'<a href="data:file/csv;base64,{b64}" download="{file_name}">Download Report</a>'
                    st.markdown(href, unsafe_allow_html=True)
                else:
                    st.info(f"No results found for '{search_date.strftime('%m/%d/%Y')}'")

        if searchtype == "Date Submitted":  # Search by date submitted

            search_date_submitted = st.date_input("Select a date of submission", key="date_sub_input")
            if search_date_submitted:
                filter_options_sub = st.radio("Filter:", ("All", "Walk-in", "Online"), index=0, key="datesubfilter")
                if filter_options_sub == "All":
                    search_results_datesub = existing_data[existing_data["DATE SUBMITTED"].str.contains(search_date_submitted.strftime('%m/%d/%Y'), case=False, na=False)]
                elif filter_options_sub == "Walk-in":
                    search_results_datesub = existing_data[(existing_data["DATE SUBMITTED"].str.contains(search_date_submitted.strftime('%m/%d/%Y'), case=False, na=False)) & (~existing_data["DATE SUBMITTED"].str.contains("ONLINE"))]
                else:
                    search_results_datesub = existing_data[(existing_data["DATE SUBMITTED"].str.contains(search_date_submitted.strftime('%m/%d/%Y'), case=False, na=False)) & (existing_data["DATE SUBMITTED"].str.contains("ONLINE"))]
                
                if not search_results_datesub.empty:
                    # Create a copy of the DataFrame before modifying it
                    search_results_datesub = search_results_datesub.copy()
                    # Convert 'CONTACT NUMBER' column to string and then replace commas
                    search_results_datesub.loc[:, "CONTACT NUMBER"] = search_results_datesub["CONTACT NUMBER"].astype(str).str.replace(',', '')
                    # Add a new column for row numbering
                    search_results_datesub.insert(0, ' ', range(1, len(search_results_datesub) + 1))
                    st.subheader(f"Search Results for '{search_date_submitted.strftime('%m/%d/%Y')}'")
                    st.write(search_results_datesub)

                    # Download button
                    csv = search_results_datesub.to_csv(index=False)
                    b64 = base64.b64encode(csv.encode()).decode()
                    file_name = f"{search_date_submitted.strftime('%m-%d-%Y')}.csv"
                    href = f'<a href="data:file/csv;base64,{b64}" download="{file_name}">Download Report</a>'
                    st.markdown(href, unsafe_allow_html=True)
                else:
                    st.info(f"No results found for '{search_date_submitted.strftime('%m/%d/%Y')}'")

        if searchtype == "Year":
            year_input = st.number_input("Search by Year", min_value=2023, max_value=2050, value=2023, step=1)
            if year_input:
                existing_data = fetch_existing_data(conn)

                # Filter the data based on the selected year
                search_results_year = existing_data[existing_data["DATE"].str.contains(str(year_input), na=False)]

                if not search_results_year.empty:
                    search_results_year = search_results_year.copy()
                    search_results_year.loc[:, "CONTACT NUMBER"] = search_results_year["CONTACT NUMBER"].astype(str).str.replace(',', '')
                    st.subheader(f"Search Results for Year {year_input}")
                    st.write(search_results_year)

                    # Download button
                    csv = search_results_year.to_csv(index=False)
                    b64 = base64.b64encode(csv.encode()).decode()
                    file_name = f"APPLICANT SUMMARY {year_input}.csv"
                    href = f'<a href="data:file/csv;base64,{b64}" download="{file_name}">Download Summary</a>'
                    st.markdown(href, unsafe_allow_html=True)
                else:
                    st.info(f"No results found for year {year_input}")
        
        if searchtype == None:
            st.info("Please select an option.")
            
    # History tab
    with tab3:
        show_history_page()
        # Link to open the google sheet
        st.link_button(label="Open Google Sheet", help="Open the Google Sheet", type="primary", url="https://docs.google.com/spreadsheets/d/1hmxu-9cIt3X8IP3OhhZRjJt_NHHqQSzjwqcEOvLadHw")

    # Analytics dataframe
    with tab4:
        show_applicants_chart(existing_data)
    
    # Feedback Form
    with tab5:
        with st.form(key="BugFeed", clear_on_submit=True, border=True):
            st.title("Feedback Form")
            st.markdown('Report a bug / Request a Feature / Provide feedback here')
            user = st.text_input(label="Author")
            title = st.text_input(label="Title")
            text = st.text_area(label="Description")
            submit = st.form_submit_button(label="Submit")
            if submit:
                if title.strip() == "" or text.strip() == "":
                    st.error(":speech_balloon: Please fill in both Title and Description.")
                else:
                    feedback_data = {
                        "User" : [user],
                        "Title": [title],
                        "Description": [text],
                        "Date Submitted": [datetime.date.today().strftime("%m/%d/%Y")]
                    }
                    update_feedback_google_sheet(conn, pd.DataFrame(feedback_data))
                    st.success("Feedback Submitted Successfully.")
    
    # Edit data tab
    with tab6:
        st.title("Edit Existing Data")
    
        # Generate random 6-digit number for authentication or retrieve from session state
        if "auth_number" not in st.session_state:
            st.session_state.auth_number = random.randint(100000, 999999)
        
        st.write(f"Please enter the following 6-digit code to unlock edit data functionality: **{st.session_state.auth_number}**")
        
        # Input field for user-entered number
        entered_number = st.number_input("Enter 6-digit Number", max_value=999999, step=1)
        if entered_number == st.session_state.auth_number:
            edit_data()
        elif entered_number != 0:
            st.error("Incorrect code.")

    # Utility Functions Tab
    with tab7:
        c1, c2 = st.columns(2)
        with c1:
            # Refresh connection button
            refresh_button = st.button(label="Refresh Connection to Google Sheets", type="secondary", help="Refresh if there are problems connecting to Google Sheets or connection is closed.", key="refresh_button")
            if refresh_button:
                refresh()
                
            # Refresh web application button
            ref_button = st.button(label="Refresh Web Application", help="Refresh the web application to update data")
            if ref_button:
                st.rerun()
        with c2:
            # Open Google Sheet button
            st.link_button(label="Open Google Sheet", help="Open the Google Sheet", type="primary", url="https://docs.google.com/spreadsheets/d/1hmxu-9cIt3X8IP3OhhZRjJt_NHHqQSzjwqcEOvLadHw")
            st.link_button(label="Documentation", help="Open Documentation", type="primary", url="https://docs.google.com/document/d/1z7xYV0r2Q0subw_HNILCXDTKl_uNttK3Nztw3ttJkd8/edit?usp=sharing")
    
    

# Hans Content
def hans_content():
    st.write(f"Welcome, {st.session_state['user']}.")
    st.title("Feedback Data")
    conn = st.connection("gsheets", type=GSheetsConnection, ttl=5)
    if conn is None:
        st.error("Failed to establish Google Sheets connection.")
        return
    if st.button("Refresh"):
        st.rerun()

    feedback_data = conn.read(worksheet="feedback", ttl=5)
    if not feedback_data.empty:
        selected_columns = ["User", "Title", "Description", "Date Submitted"]
        feedback_data = feedback_data[selected_columns]
        st.write(feedback_data)
    else:
        st.info("No feedback data available.")

    # Logout button
    if st.button("Logout"):
        st.write("Logging Out...")
        del st.session_state["user"]
        time.sleep(1)
        st.rerun()

# Main Page
def show_main_page():
    if st.session_state["user"] == "Hans":
        hans_content()
    else:
        main_content()      


# Initially run the main function when web app is opened
if __name__ == "__main__":
    main()
