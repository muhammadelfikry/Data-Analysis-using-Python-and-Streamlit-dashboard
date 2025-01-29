import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
sns.set(style="dark")

# helper
def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule="D", on="dteday").agg({
        "cnt": "sum",
        "casual": "sum",
        "registered": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "cnt": "Total_transaction"
    }, inplace=True)
    
    return daily_orders_df

def create_monthly_orders_df(df):
    monthly_orders = df.groupby(by=pd.Grouper(key="dteday", freq="ME")).cnt.sum()
    monthly_orders.index = monthly_orders.index.strftime("%Y-%m")
    monthly_orders = monthly_orders.reset_index()
    
    return monthly_orders

def create_quarter_orders_df(df):
    quarter_orders_df = df.groupby(by=pd.Grouper(key="dteday", freq="QE")).agg({
        "casual": "sum",
        "registered": "sum"
    }).reset_index()
    
    return quarter_orders_df

def create_season_orders_df(df):
    season_orders_df = df.groupby(by=[pd.Grouper(key="dteday", freq="YE"), "season"]).cnt.sum().reset_index()
    
    return season_orders_df

def create_weathersit_df(df):
    weathersit_orders = df.groupby(by=[pd.Grouper(key="dteday", freq="ME"), "weathersit"]).cnt.sum().reset_index()
    
    return weathersit_orders

def create_cluster_df(df):
    cluster_df = df.groupby(by=pd.Grouper(key="dteday", freq="ME")).cnt.sum().reset_index()

    mean_value = cluster_df["cnt"].mean()
    std_value = cluster_df["cnt"].std()

    cluster_df["category"] = pd.cut(
        cluster_df["cnt"],
        bins=[0, mean_value, mean_value + std_value, float("inf")],
        labels=["Low Transaction", "Medium Transaction", "High Transaction"]
    )

    return cluster_df

# load dataset
day_df = pd.read_csv("dashboard/dataset/day.csv")
monthly_df = pd.read_csv("dashboard/dataset/monthly.csv")
quarter_df = pd.read_csv("dashboard/dataset/quarter.csv")
cluster_df = pd.read_csv("dashboard/dataset/cluster.csv")
season_df = pd.read_csv("dashboard/dataset/season.csv")
weathersit_df = pd.read_csv("dashboard/dataset/weathersit.csv")

day_df["dteday"] = pd.to_datetime(day_df["dteday"])
monthly_df["dteday"] = pd.to_datetime(monthly_df["dteday"])
quarter_df["dteday"] = pd.to_datetime(quarter_df["dteday"])
cluster_df["dteday"] = pd.to_datetime(cluster_df["dteday"])
season_df["dteday"] = pd.to_datetime(season_df["dteday"])
weathersit_df["dteday"] = pd.to_datetime(weathersit_df["dteday"])

# filter
monthly_min_date = monthly_df["dteday"].min()
monthly_max_date = monthly_df["dteday"].max()

cluster_min_date = cluster_df["dteday"].min()
cluster_max_date = cluster_df["dteday"].max()

quarter_min_date = quarter_df["dteday"].min()
quarter_max_date = quarter_df["dteday"].max()

season_min_date = season_df["dteday"].min()
season_max_date = season_df["dteday"].max()

weathersit_min_date = weathersit_df["dteday"].min()
weathersit_max_date = weathersit_df["dteday"].max()

# sidebar
with st.sidebar:
    st.title("Menu")

    select_box= st.selectbox(
        label="Select data category",
        options=("Monthly Orders", "Quarter Orders", "Season orders", "Weathersit Orders", "Cluster Orders")
    )

    option_labels = {"Monthly Orders": [monthly_min_date, monthly_max_date], 
                     "Quarter Orders": [quarter_min_date, quarter_max_date], 
                     "Season orders": [season_min_date, season_max_date], 
                     "Cluster Orders": [cluster_min_date, cluster_max_date],
                     "Weathersit Orders": [weathersit_min_date, weathersit_max_date]}
    
    if select_box in option_labels:
        start_date, end_date = st.date_input(
            label="Range", 
            min_value=option_labels[select_box][0],
            max_value=option_labels[select_box][1],
            value=option_labels[select_box]
        )

# dataframe
monthly_df = monthly_df[(monthly_df["dteday"] >= str(start_date)) &
                        (monthly_df["dteday"] <= str(end_date))]

season_df = season_df[(season_df["dteday"] >= str(start_date)) &
                        (season_df["dteday"] <= str(end_date))]

quarter_df = quarter_df[(quarter_df["dteday"] >= str(start_date)) &
                        (quarter_df["dteday"] <= str(end_date))]

cluster_df = cluster_df[(cluster_df["dteday"] >= str(start_date)) &
                        (cluster_df["dteday"] <= str(end_date))]

weathersit_df = weathersit_df[(weathersit_df["dteday"] >= str(start_date)) &
                              (weathersit_df["dteday"] <= str(end_date))]

daily_orders_df = create_daily_orders_df(day_df)
monthly_orders_df = create_monthly_orders_df(monthly_df)
season_orders_df = create_season_orders_df(season_df)
quarter_orders_df = create_quarter_orders_df(quarter_df)
cluster_orders_df = create_cluster_df(cluster_df)
weathersit_orders_df = create_weathersit_df(weathersit_df)

# Dashboard
st.title("Dashboard")

with st.container():
    col1, col2, col3 = st.columns(3)

    with col1:
        total_transaction = daily_orders_df["Total_transaction"].sum()
        st.metric("Total Transaction", value=total_transaction)

    with col2:
        total_casual = daily_orders_df.casual.sum()
        st.metric("Total Casual Customers", value=total_casual)

    with col3:
        total_registered = daily_orders_df.registered.sum()
        st.metric("Total Registered Customers", value=total_registered)

with st.container():
    if select_box == "Monthly Orders":
        st.header("Monthly Orders")
        data = monthly_orders_df
        data.set_index("dteday", inplace=True)
        st.line_chart(data)

    elif select_box == "Quarter Orders":
        q_orders_melted = quarter_orders_df.melt(id_vars=["dteday"], var_name="customer_type", value_name="count")
        
        st.header("Transactions by Customer Type each Quarter")
        plt.figure(figsize=(10,6))
        sns.barplot(data=q_orders_melted, x="dteday", y="count", hue="customer_type")
        plt.xlabel(None)
        plt.ylabel(None)
        plt.xticks(rotation=45)
        st.pyplot(plt)

    elif select_box == "Season orders":
        st.header("Total Transactions per Season (Grouped by year)")
        plt.figure(figsize=(8, 5))
        sns.barplot(data=season_orders_df, x="dteday", y="cnt", hue="season", palette="viridis")
        plt.xlabel(None)
        plt.ylabel(None)
        plt.legend(title="Season", loc="best")
        st.pyplot(plt)

    elif select_box == "Weathersit Orders":
        st.header("Total Transactions Grouped by weathersit (monthly)")
        plt.figure(figsize=(15, 6))
        sns.barplot(data=weathersit_orders_df, x="dteday", y="cnt", hue="weathersit", palette="viridis")
        plt.xlabel(None)
        plt.ylabel(None)
        plt.legend(title="weathersit", loc="best")
        plt.xticks(rotation=45)
        st.pyplot(plt)

    elif select_box == "Cluster Orders":
        st.header("Transaction segmentation")

        low_transaction_df = cluster_orders_df[cluster_orders_df["category"] == "Low Transaction"]
        medium_transaction_df = cluster_orders_df[cluster_orders_df["category"] == "Medium Transaction"]
        high_transaction_df = cluster_orders_df[cluster_orders_df["category"] == "High Transaction"]
        
        st.subheader("Low Transaction (mounth)")

        fig, ax = plt.subplots(figsize=(20, 10))
        sns.barplot(data=low_transaction_df, x="dteday", y="cnt")
        ax.set_ylabel(None)
        ax.set_xlabel(None)
        ax.tick_params(axis="x", rotation=45)

        st.pyplot(fig)

        st.subheader("Medium Transaction (mounth)")
        
        fig, ax = plt.subplots(figsize=(20, 10))
        sns.barplot(data=medium_transaction_df, x="dteday", y="cnt", color="orange")
        ax.set_ylabel(None)
        ax.set_xlabel(None)
        ax.tick_params(axis="x", rotation=45)
        
        st.pyplot(fig)

        st.subheader("High Transaction (mounth)")

        fig, ax = plt.subplots(figsize=(20, 10))
        sns.barplot(data=high_transaction_df, x="dteday", y="cnt", color="green")
        ax.set_ylabel(None)
        ax.set_xlabel(None)
        ax.tick_params(axis="x", rotation=45)
        
        st.pyplot(fig)
