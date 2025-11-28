import streamlit as st
import pandas as pd
import mysql.connector as db
from datetime import datetime

connection = db.connect(
    host = "localhost",
    user = 'shaik',
    password = 'Password@000',
    database = 'qms',
    autocommit = True
)

cursor = connection.cursor()

if "page" not in st.session_state:
    st.session_state.page = "login"


def login_page():

    def check_credentials(username, password,selected_role):
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user_info WHERE BINARY username=%s AND BINARY password=%s AND BINARY role=%s", (username, password,selected_role))
        result = cursor.fetchone()
        return result is not None

            
    st.markdown("##### Shaik's Query Management System")
    st.markdown("#### Login")

    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")
    selected_role = st.selectbox("Select Role", ["Please choose a role", "Client", "Support"], index = 0)


    if st.button('Sign In'):
        if check_credentials(username, password,selected_role):
            st.success('Login successful')
            if selected_role == "Client":
                st.session_state.page = "client"
                st.rerun()
            
            elif selected_role == "Support":
                st.session_state.page = "support"
                st.rerun()

        else:
            st.warning("invalid credentials")

   
def client_page():

    def date_time():
        now = datetime.now()
        date = now.strftime("%d-%m-%Y")
        time = now.strftime("%I:%M %p")
        return date + ' ' + time

    def insert():
        values = (email_id, mobile_number, Query_heading, Query_description, status, query_created_time, query_closed_time)
        ins_q = """
        insert into query (email_id, mobile_number, query_heading, query_description, status, query_created_time, query_closed_time)
        values
        (%s,%s,%s,%s,%s,%s,%s)
        """
        cursor.execute( ins_q, tuple(values))
        


    st.markdown("#### Create a Query")


    email_id = st.text_input("Email ID:")
    mobile_number = st.text_input("Mobile number:")
    Query_heading = st.text_input("Query Heading:")
    Query_description = st.text_area("Query Description:")
    status = "open"
    query_closed_time = None
    


    if st.button("Submit"):
        if all([email_id.strip(), mobile_number.strip(), Query_heading.strip(), Query_description.strip()]):
            
            query_created_time = date_time()
            
            insert()

            generated_id = cursor.lastrowid
            st.markdown(
            f"""
            <h2 style='font-size: 18px; color: green; font-weight: 400;'>
                Your query has been submitted! Your Query ID is {generated_id}.
            </h2>
            """,
            unsafe_allow_html=True
            )

        else:
            st.error("Please enter all the details!")


    if st.button("Logout"):
        st.session_state.page = "login"
        st.session_state.role = None
        st.rerun()


def support_page():

    def date_time(query_id):
        now = datetime.now()
        date = now.strftime("%d-%m-%Y")
        time = now.strftime("%I:%M %p")
        query_closed_time =  date + ' ' + time
        update_time_q = """
                UPDATE query 
                SET query_closed_time =  %s
                WHERE query_id = %s          
        """
        cursor.execute(update_time_q, (query_closed_time, query_id))



    def close_query(query_id):
        update_q = """
            UPDATE query 
            SET status = 'closed' 
            WHERE query_id = %s
        """
        cursor.execute(update_q, (query_id,))
        

    def status_open():
        open_q = """select * from query where status = 'open'"""
        cursor.execute(open_q)
        data_open = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        df_open = pd.DataFrame(data_open, columns=columns)

        df_open['Close_Query'] = False

        edited_df = st.data_editor(
        df_open,
        column_config={
            "Close_Query": st.column_config.CheckboxColumn(
                "Close Query",
                help="Check to close this query",
            )
        },
        hide_index=True,
        )

        for index, row in edited_df.iterrows():
            if row["Close_Query"]:
                query_id = row["QUERY_ID"]
                date_time(query_id)   
                close_query(query_id)
                st.rerun()

        open_query_len = len(edited_df)

        st.markdown(
            f"""
            <h2 style='font-size: 18px; color: green; font-weight: 400;'>
                Total Open Queries: {open_query_len}.
            </h2>
            """,
            unsafe_allow_html=True
            )

        
    def status_closed():
        closed_q = """select * from query where status = 'closed'"""
        cursor.execute(closed_q)
        data_closed = cursor.fetchall()

        columns = [col[0] for col in cursor.description]
        df_closed = pd.DataFrame(data_closed, columns=columns)
        st.write(df_closed) 

        closed_query_len = len(df_closed)

        st.markdown(
            f"""
            <h2 style='font-size: 18px; color: green; font-weight: 400;'>
                Total Closed Queries: {closed_query_len}.
            </h2>
            """,
            unsafe_allow_html=True
            )

    st.markdown("### Address Client Queries")
    st.markdown("###### To close the query, click the checkbox in the last column.")
    query_status = st.radio('Choose the query status to view', ['open','closed'])

    if query_status == 'open':
        status_open()
    elif query_status == "closed":
        status_closed()


    if st.button("Logout"):
        st.session_state.page = "login"
        st.session_state.role = None
        st.rerun()


if st.session_state.page == "login":
    login_page()

elif st.session_state.page == "client":
    client_page()

elif st.session_state.page == "support":
    support_page()

cursor.close()
connection.close()