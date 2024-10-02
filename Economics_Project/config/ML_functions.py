import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.optimizers import Adam

def prepare_data(data, target_column, look_back=60):
    if isinstance(data, pd.Series):
        data = data.to_frame()
    
    scaler = StandardScaler()
    if data.shape[1] == 1:
        scaled_data = scaler.fit_transform(data)
    else:
        scaled_data = scaler.fit_transform(data)
        target_idx = data.columns.get_loc(target_column)
    
    X, y = [], []
    for i in range(look_back, len(scaled_data)):
        X.append(scaled_data[i-look_back:i])
        y.append(scaled_data[i, target_idx if data.shape[1] > 1 else 0])
    
    return np.array(X), np.array(y), scaler

def create_lstm_model(input_shape):
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=input_shape),
        LSTM(50, return_sequences=False),
        Dense(25),
        Dense(1)
    ])
    model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')
    return model

def train_and_evaluate(X, y, test_size=0.2, epochs=100, batch_size=32):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, shuffle=False)
    
    model = create_lstm_model((X_train.shape[1], X_train.shape[2]))
    model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_split=0.1, verbose=0)
    
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    return model, y_pred, mse, r2

def predict_future(model, last_sequence, scaler, n_steps=30):
    future_predictions = []
    current_sequence = last_sequence.copy()
    
    for _ in range(n_steps):
        scaled_prediction = model.predict(current_sequence.reshape(1, *current_sequence.shape))
        future_predictions.append(scaled_prediction[0, 0])
        current_sequence = np.roll(current_sequence, -1, axis=0)
        current_sequence[-1] = scaled_prediction
    
    future_predictions = np.array(future_predictions).reshape(-1, 1)
    if scaler.n_features_in_ == 1:
        return scaler.inverse_transform(future_predictions)
    else:
        inverse_predictions = np.zeros((len(future_predictions), scaler.n_features_in_))
        inverse_predictions[:, 0] = future_predictions.flatten()
        return scaler.inverse_transform(inverse_predictions)[:, 0].reshape(-1, 1)
    
def evaluate_model(y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    return mae, mse, rmse, mape