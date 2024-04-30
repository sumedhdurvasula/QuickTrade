from turtle import update
import streamlit as st
import json
import os
from tensorflow.keras.models import load_model
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
from tensorflow.keras.models import Model
import yfinance as yf
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import matplotlib.pyplot as plt
from datetime import datetime

st.title('Welcome to QUICKTrade stock page')

st.text('Here is where you can run our model to predict the fluctuation of a stock.\n\n')

st.text('Enter a stock ticker to see what how it will move in the next couple days!')

def save_model(model, filename):
    model.save(filename)
def download_data(stock_symbol, start_date, end_date):
    data = yf.download(stock_symbol, start=start_date, end=end_date)
    return data['Close'].values.reshape(-1, 1)  

def normalize_data(data):
    mean = np.mean(data, axis=0)
    std = np.std(data, axis=0)
    return (data - mean) / std, mean, std

def prepare_data(data, n_steps):
    X, y = [], []
    for i in range(n_steps, len(data)):
        X.append(data[i-n_steps:i])
        y.append(data[i])
    return np.array(X), np.array(y)

def runModel(ticker):
    print("Running runModel")
    raw_data = download_data(ticker, '2023-01-01', '2024-04-01')
    normalized_data, data_mean, data_std = normalize_data(raw_data)

    n_steps = 10
    X, y = prepare_data(normalized_data, n_steps)

    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(n_steps, 1)),
        Dropout(0.2),
        LSTM(50, return_sequences=True),
        Dropout(0.2),
        LSTM(50, return_sequences=False),
        Dropout(0.2),
        Dense(1)
    ])

    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2)
    predictions = model.predict(X_test)
    predictions = predictions * data_std + data_mean

    def decompose_weights(weights, rank):
        U, S, Vt = np.linalg.svd(weights, full_matrices=False)
        S = np.diag(S)[:rank, :rank]
        U = U[:, :rank]
        Vt = Vt[:rank, :]
        return U, S, Vt
    def reconstruct_matrix(U, S, Vt):
        return np.dot(U, np.dot(S, Vt))
    def apply_low_rank_compression(model, rank):
        for layer in model.layers:
            if 'dense' in layer.name:
                original_weights = layer.get_weights()
                if len(original_weights) > 0:
                    W = original_weights[0]
                    b = original_weights[1]
                    U, S, Vt = decompose_weights(W, rank)
                    W_compressed = reconstruct_matrix(U, S, Vt)
                    layer.set_weights([W_compressed, b])
        return model

    rank = 10 
    model_compressed = apply_low_rank_compression(model, rank)
    model_compressed.compile(optimizer='adam', loss='mean_squared_error')
    filenameComp = 'compressed_model_{variable}.h5'.format(variable=ticker)
    save_model(model_compressed, 'models/' + filenameComp)

    current_date = datetime.now().strftime('%Y-%m-%d')
    raw_data = yf.download(ticker, start='2024-04-02', end=current_date)['Close'].values.reshape(-1, 1)
    data_mean = np.mean(raw_data)
    data_std = np.std(raw_data)
    normalized_data = (raw_data - data_mean) / data_std
    n_steps = 10
    X = []
    for i in range(n_steps, len(normalized_data)):
        X.append(normalized_data[i-n_steps:i])
    X = np.array(X)
    latest_data = normalized_data[-n_steps:]
    future_prices = []
    for i in range(10):
        prediction = model.predict(latest_data.reshape(1, -1, 1))
        future_price = prediction.flatten()[-1] * data_std + data_mean
        future_prices.append(future_price)
        latest_data = np.append(latest_data[1:], prediction)
    final_price = future_prices[-1]
    data = yf.download(ticker, period='1d')
    recent_price = data['Close'].values[-1]
    return ((final_price/recent_price) - 1) * 100

# temp = runModel('MSFT')

def predict_future_stock_price(filepath,  ticker ,steps=10):
    model = load_model(filepath)
    current_date = datetime.now().strftime('%Y-%m-%d')
    raw_data = yf.download(ticker, start='2024-04-02', end=current_date)['Close'].values.reshape(-1, 1)
    data_mean = np.mean(raw_data)
    data_std = np.std(raw_data)
    normalized_data = (raw_data - data_mean) / data_std

    n_steps = 10
    X = []
    for i in range(n_steps, len(normalized_data)):
        X.append(normalized_data[i-n_steps:i])
    X = np.array(X)
    latest_data = normalized_data[-n_steps:]
    future_prices = []
    for i in range(steps):
        prediction = model.predict(latest_data.reshape(1, -1, 1))
        future_price = prediction.flatten()[-1] * data_std + data_mean
        future_prices.append(future_price)
        latest_data = np.append(latest_data[1:], prediction)
    final_price = future_prices[-1]
    data = yf.download(ticker, period='1d')
    recent_price = data['Close'].values[-1]
    return ((final_price/recent_price) - 1) * 100



def update_ticker_count(filename, ticker):
    try:
        with open("data/"+ filename + ".json", 'r') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    if ticker in data:
        data[ticker] += 1
    else:
        data[ticker] = 1
    with open("data/" + filename + ".json", 'w') as file:
        json.dump(data, file, indent=4)

def get_model_files():
    models_dir = 'models'
    model_files = [f for f in os.listdir(models_dir) if os.path.isfile(os.path.join(models_dir, f))]
    return model_files

tick = st.text_input("Enter a stock ticker")

if tick:
    st.write(f'You entered: {tick}')
    if st.button('Is there a model to predict the price on?'):
        model_files = get_model_files()
        if model_files:
            model_choice = st.selectbox("Choose a model to use:", model_files)
            st.write("Percent Change in the next week", round(predict_future_stock_price('models/' + str(model_choice), tick),4),"%")
        
       
    if st.button('Train and Run'):
        print("Running Testing")
        st.write("Percent Change in the next week", round(runModel(tick),4),"%")

    st.text('Have you invested in this stock recently?')
    if st.button('Yes'):
        st.write('Great!')
        if 'username' in st.session_state:
            this_port = st.session_state.port
            update_ticker_count(st.session_state.username + str(this_port), tick.upper())
            st.markdown('Click on the Users page to find more people with your interests.')   
        else:
            st.write("Please login to continue updating your investment history")
    elif st.button('No'):
        st.write('Go to the recommendations page to find new Stocks!')