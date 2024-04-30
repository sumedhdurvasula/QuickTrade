import streamlit as st
import json
import pandas as pd

st.title('Welcome to QUICKTrade history page')

this_port = st.session_state.port

def update_ticker_count(filename, ticker, val):
    try:
        with open("data/"+ filename + ".json", 'r') as file:
            data = json.load(file)
        this_port = st.session_state.port
        target_host = "localhost"
        my_peers = [8501, 8502, 8503, 8504, 8505]
        my_peers.remove(this_port)
        for target_port in my_peers:
            print("Trying to connect to port " + str(target_port))
            try:
                st.session_state.my_peer.connect_to_peer(target_host, target_port)
                file_path = 'data/' + st.session_state.username + str(st.session_state.port) + '.json'  
                st.session_state.my_peer.send_file_to_peer(target_host, target_port, file_path)
                st.success("Connection Established and File sent!")
            except Exception as e:
                print("No peer yet at port " + str(target_port) + " (or file error)")
                continue

    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    data[ticker] = val
    with open("data/" + filename + ".json", 'w') as file:
        json.dump(data, file, indent=4)

def resetCount(filename):
    try:
        with open("data/"+ filename + ".json", 'r') as file:
            data = json.load(file)

        this_port = st.session_state.port
        target_host = "localhost"
        my_peers = [8501, 8502, 8503, 8504, 8505]
        my_peers.remove(this_port)
        for target_port in my_peers:
            print("Trying to connect to port " + str(target_port))
            try:
                st.session_state.my_peer.connect_to_peer(target_host, target_port)
                file_path = 'data/' + st.session_state.username + str(st.session_state.port) + '.json'  
                st.session_state.my_peer.send_file_to_peer(target_host, target_port, file_path)
                st.success("Connection Established and File sent!")
            except Exception as e:
                print("No peer yet at port " + str(target_port) + " (or file error)")
                continue
            
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    data = {}
    with open("data/" + filename + ".json", 'w') as file:
        json.dump(data, file, indent=4)

if 'username' in st.session_state and st.session_state.username:
    try:
        with open('data/' + st.session_state.username + str(st.session_state.port)+ '.json', 'r') as file:
            data_dict = json.load(file)
        
        table_data = [{'Ticker': ticker, 'Count': count} for ticker, count in data_dict.items()]
        df = pd.DataFrame(table_data)
        df = df.sort_values(by='Ticker', ascending=True)

        st.subheader('Stock Ticker Counts')
        st.table(df.reset_index(drop=True))
    except FileNotFoundError:
        st.error('User file not found.')
    except json.JSONDecodeError:
        st.error('Error decoding JSON file.')
    except Exception as e:
        st.write("Enter your first stock!")
    with st.form(key='ticker_input'):
        input_string = st.text_input("Enter the Ticker and the number of times you invested (ex. appl,2):")
        submit_button = st.form_submit_button(label='Update')
        if submit_button:
            try:
                tick, count_str = input_string.split(',')
                count = int(count_str)
                update_ticker_count(st.session_state.username + str(this_port), tick.strip().upper(), count)
                st.success("Ticker count updated successfully!")
                st.experimental_rerun()
            except ValueError:
                st.error("Please enter a valid ticker and count, separated by a comma.")
            except IndexError:
                st.error("Please enter the ticker and count separated by a comma.")

    if st.button('Reset Investments'):
        resetCount(st.session_state.username + str(this_port))
        st.text('Investments have been reset.')
        st.experimental_rerun()
        
else: 
    st.text("Please login")
