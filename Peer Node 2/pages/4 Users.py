import streamlit as st
import os
import json
import pandas as pd
import re
from math import sqrt
import datetime

st.title('Welcome to QUICKTrade user page')

def dot_product(v1, v2):
    return sum(v1.get(k, 0) * v2.get(k, 0) for k in set(v1) | set(v2))

def magnitude(v):
    return sqrt(sum(val**2 for val in v.values()))

def cosine_similarity(dict1, dict2):
    dot = dot_product(dict1, dict2)
    mag1 = magnitude(dict1)
    mag2 = magnitude(dict2)
    return dot / (mag1 * mag2) if mag1 and mag2 else 0

def timestamp_message(action):
    now = datetime.datetime.now()
    formatted_time = now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"{action} at {formatted_time}")

try:
    user_json_path = 'data/' + st.session_state.username + str(st.session_state.port) + '.json'
    directory_path = 'received'

    with open(user_json_path, 'r') as user_file:
        current_user_data = json.load(user_file)

    files_in_directory = os.listdir(directory_path)
    json_files = [file for file in files_in_directory if file.endswith('.json')]

    user_data = []

    try:
        for json_file in json_files:
            file_path = os.path.join(directory_path, json_file)
            with open(file_path, 'r') as file:
                other_user_data = json.load(file)
                port = json_file[-9:-5]
                username = json_file[9:-9]
                similarity_score = cosine_similarity(current_user_data, other_user_data)
                user_data.append({
                    'User': username,
                    'Portfolio Similarity Score': similarity_score,
                    'Port': port
                })

        df = pd.DataFrame(user_data)
        df = df.sort_values(by='Portfolio Similarity Score', ascending=False)
        st.table(df.reset_index(drop=True))

        target_host = st.text_input("Peer Host", "localhost")
        username = st.selectbox("Choose the user you want to chat with:", df['User'].unique())
        models_path = 'models/'
        model_files = [f for f in os.listdir(models_path) if os.path.isfile(os.path.join(models_path, f))]

        model = st.selectbox("Choose the model file:", model_files)
        if username:
            destport = df[df['User'] == username]['Port'].values[0]
        if st.button("Send Model to Peer"):
            st.session_state.my_peer.send_file_to_peer(target_host, destport, models_path+ model)
            st.success("Model sent!")
            timestamp_message("Message Sent!")
        
        
        
#         message = st.text_area("Message to Send")
#         if st.button("Send Message"):
#             st.session_state.my_peer.send_to_peer(target_host, destport, message)
#             st.success("Message sent!")

#         messages = st.session_state.my_peer.get_messages()

#         if messages:
#             st.subheader("Sent and Received Messages")
#             for sender, messages_list in messages.items():
#                 for message in messages_list:
#                     st.write(message)
#         else:
#             st.write("No messages sent or received yet.")
    except:
        st.write("No files received yet.")
except:
     st.write("Please login and wait for peers to view this page.")