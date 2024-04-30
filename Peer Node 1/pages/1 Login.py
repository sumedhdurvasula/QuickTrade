import streamlit as st
import json

def load_logins(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {'test': 'test'}

def save_logins(file_path, logins_dict):
    with open(file_path, 'w') as file:
        json.dump(logins_dict, file)

if 'logins' not in st.session_state:
    st.session_state.logins = load_logins('data/logins.json')

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title('Welcome to QUICKTrade')
    st.write("Please log in to continue. Use email to login or rgister a new account.")

    username = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Log in"):
        if (username in st.session_state.logins and 
            password == st.session_state.logins[username]):
            st.session_state.username = username
            st.session_state.logged_in = True
            st.success("Logged in successfully!")
            st.experimental_rerun()
        else:
            st.error("Incorrect username or password")

    with st.expander("Register new account"):
        new_username = st.text_input("Choose a username", key="reg_username")
        new_password = st.text_input("Choose a password", type="password", key="reg_password")
        confirm_password = st.text_input("Confirm password", type="password", key="confirm_password")
        if st.button("Register", key="register"):
            if new_username in st.session_state.logins:
                st.error("Username already exists. Please choose a different one.")
            elif not new_username or not new_password:
                st.error("Username and password cannot be empty.")
            elif new_password != confirm_password:
                st.error("Passwords do not match. Please try again.")
            else:
                st.session_state.logins[new_username] = new_password
                save_logins('data/logins.json', st.session_state.logins)
                save_logins("data/" + new_username + ".json", {})
                st.success("Account created successfully! You can now log in.")
else:
    st.write(f"Welcome, {st.session_state.username}!")
