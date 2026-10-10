
import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt
reg_model = joblib.load("regression_model.pkl")
reg_scaler = joblib.load("regression_scaler.pkl")
cls_model = joblib.load("classification_model.pkl")
cls_scaler = joblib.load("classification_scaler.pkl")
clustered_data = pd.read_csv("clustered_data.csv")

st.title("HỆ THỐNG DỰ ĐOÁN SẢN PHẨM")

st.header("Nhập thông tin")

values = [
    st.number_input("Kích thước màn hình", value=6.5),
    st.number_input("RAM (GB)", value=8.0),
    st.number_input("ROM (GB)", value=128.0),
    st.number_input("Năm phát hành", value=2024),
    st.number_input("Rating", 0.0, 5.0, 4.5),
    st.number_input("Số lượt đánh giá", value=100),
    st.number_input("Lượt xem/tháng", value=1000),
    st.number_input("Đơn hàng/tháng", value=100),
    st.number_input("Đánh giá khách hàng", 0.0, 5.0, 4.5),
    st.number_input("Tồn kho", value=100)
]

features = [
    "screen_size", "ram", "rom", "release_year", "rating",
    "num_reviews", "monthly_views", "monthly_orders",
    "customer_rating", "stock_quantity"
]

input_data = pd.DataFrame([values], columns=features)

if st.button("Dự đoán giá"):
    x = reg_scaler.transform(input_data)
    result = reg_model.predict(x)[0]
    st.success(f"Giá dự đoán: {result:,.0f}")

if st.button("Phân loại giá"):  
    x = cls_scaler.transform(input_data)
    result = cls_model.predict(x)[0]
    st.success(f"Nhóm giá: {result}")

st.header("K-Means")

if "Cluster_Label" in clustered_data.columns:
    counts = clustered_data["Cluster_Label"].value_counts().sort_index()
    st.bar_chart(counts)
    st.dataframe(clustered_data.head(20))
