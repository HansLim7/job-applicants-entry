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

# Set page configurations here
st.set_page_config(
    page_title="JobApplicantsInfo",
    page_icon="🖊",
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
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        show_login_page()
    else:
        show_main_page()

# Login page
def show_login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    Un = "CHRMO"  # Username
    Pass = "1234" # Password

    login_button = st.button(label="Login", type="primary")
    if login_button:
        if username == Un and password == Pass:  # Check if credentials are correct
            st.session_state.authenticated = True
            st.success("Logged in, Click on 'login' again to proceed.")
        else:
            st.error("Invalid username or password. Please try again.")

# Gather the last 10 entries in the google sheet
def fetch_last_ten_entries(conn):
    existing_data = fetch_existing_data(conn)
    last_ten_entries = existing_data.tail(10)  # Get the last ten entries
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

    last_ten_entries = fetch_last_ten_entries(conn)
    if st.button("Refresh"):
        st.rerun()
    st.write(last_ten_entries)
        

# Fetch existing data in the google sheet
def fetch_existing_data(conn):
    existing_data = conn.read(worksheet="Applicants", usecols=list(range(12)), ttl=5)
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

# Main Content
def show_main_page():
    st.title("🖊 Job Applicants' Information 🖊")
    conn = st.connection("gsheets", type=GSheetsConnection, ttl=5)  # Connect to google sheets
    existing_data = fetch_existing_data(conn)  # Initially get all of the current data from the sheet
    
   # Main content expander
    with st.expander(label="Enter new Applicant"):
        # Display form for entering new applicant information
        with st.form(key="Applicants", clear_on_submit=True, border=True):
            st.markdown('**Fields marked with ( * ) are Required.**')
            # Ask the user if the submission is online or not
            online_submission = st.checkbox("Online Submission")
            
            # Divide the form into two columns
            col1, col2 = st.columns(2) 
        
            with col1: # Left column
                date = st.date_input(label="Date*", help="Select Date.", format="MM/DD/YYYY")
                name = st.text_input(label="Name of Applicant*", help="Full Name")
                desired_position = st.text_input(label="Desired Position", help="'Any Vacant Position' if not provided.")
                address = st.text_input(label="Address")
                birthday_or_age = st.text_input(label="Date of Birth or Age", help="Enter Birthday in MM/DD/YYYY format or Age directly", placeholder="Enter date of birth (mm/dd/yyy) or age")
                gender = st.selectbox(label="Gender", options=["MALE", "FEMALE", "OTHER"], index=None, placeholder="Select Gender")
                current_pos = st.text_input(label="Current Position", help="leave blank if N/A")
            
            with col2: # Right column
                date_submitted = st.date_input(label="Date Submitted*", help="Select Date Submitted", value=None, format="MM/DD/YYYY")
                contact_number = st.text_input(label="Contact Number", help="Numeric only", max_chars=11)
                forwarded_from = st.text_input(label="Forwarded From", help="CHRMO")
                educational_attainment = st.text_area(label="Educational Attainment")
                csc_eligibility = st.text_area(label="CSC Eligibility", help="Leave blank if N/A")

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


    # Search by Name Expander
    with st.expander("Search by Name"):
        search_name = st.text_input("Enter name", key="name_input")
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
        
    # Search by Date Expander
    with st.expander("Search by Date"):
        search_date = st.date_input("Select a date", key="date_input")
        if search_date:
            search_results_date = existing_data[existing_data["DATE"].str.contains(search_date.strftime('%m/%d/%Y'), case=False, na=False)]
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
                href = f'<a href="data:file/csv;base64,{b64}" download="{file_name}">Download</a>'
                st.markdown(href, unsafe_allow_html=True)
            else:
                st.info(f"No results found for '{search_date.strftime('%m/%d/%Y')}'")

    # Search by Date Submitted Expander
    with st.expander("Search by Date Submitted"):
        search_date_submitted = st.date_input("Select a date of submission", key="date_sub_input")
        if search_date_submitted:
            search_results_datesub = existing_data[existing_data["DATE SUBMITTED"].str.contains(search_date_submitted.strftime('%m/%d/%Y'), case=False, na=False)]
            if not search_results_datesub.empty:
                # Create a copy of the DataFrame before modifying it
                search_results_datesub = search_results_datesub.copy()
                search_results_datesub.loc[:, "CONTACT NUMBER"] = search_results_datesub["CONTACT NUMBER"].astype(str).str.replace(',', '')
                # Add a new column for row numbering
                search_results_datesub.insert(0, ' ', range(1, len(search_results_datesub) + 1))
                st.subheader(f"Search Results for '{search_date_submitted.strftime('%m/%d/%Y')}'")
                st.write(search_results_datesub)

                # Download button
                csv = search_results_datesub.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                file_name = f"{search_date_submitted.strftime('%m-%d-%Y')}.csv"
                href = f'<a href="data:file/csv;base64,{b64}" download="{file_name}">Download</a>'
                st.markdown(href, unsafe_allow_html=True)
            else:
                st.info(f"No results found for '{search_date_submitted.strftime('%m/%d/%Y')}'")

    # History Expander
    with st.expander("History (Last 10 Entries)"):
        show_history_page()
        # Link to open the google sheet
        st.link_button(label="Open Google Sheet", help="Open the Google Sheet", type="primary", url="https://docs.google.com/spreadsheets/d/1rHQ924Hn3W4Au_4k90nXr86TlwPZ-JY8wonjO1eJF4Y")
             
    # Feedback Form
    with st.expander("Report a Bug / Feedback"):
        with st.form(key="BugFeed", clear_on_submit=True, border=False):
            st.markdown('Report a bug / Request a Feature / Provide feedback here')
            title = st.text_input(label="Title")
            text = st.text_area(label="Description")
            submit = st.form_submit_button(label="Submit")
            if submit:
                if title.strip() == "" or text.strip() == "":
                    st.error("Please fill in both Title and Description.")
                else:
                    feedback_data = {
                        "Title": [title],
                        "Description": [text],
                        "Date Submitted": [datetime.date.today().strftime("%m/%d/%Y")]
                    }
                    update_feedback_google_sheet(conn, pd.DataFrame(feedback_data))
                    st.success("Feedback Submitted Successfully.")

            
    # Create another set of columns for refreshing gsheets connection and web app
    c1, c2, c3 = st.columns(3)
    with c1:
        # Refresh connection button
        refresh_button = st.button(label="Refresh Connection to Google Sheets", type="secondary", help="Refresh if there are problems connecting to Google Sheets or connection is closed.", key="refresh_button")
        if refresh_button:
            refresh()
    with c2:
        ref_button = st.button(label = "Refresh web application", help="Refresh the web application to update data")
        if ref_button:
            st.rerun()
    with c3:
        st.link_button(label="Open Google Sheet", help="Open the Google Sheet", type="primary", url="https://docs.google.com/spreadsheets/d/1rHQ924Hn3W4Au_4k90nXr86TlwPZ-JY8wonjO1eJF4Y")
        
# Initially run the main function when web app is opened
if __name__ == "__main__":
    main()
