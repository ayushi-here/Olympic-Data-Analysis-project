import streamlit as st
import pandas as pd
import preprocessor
import helper
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff

st.set_page_config(page_title="Olympic Insights", layout="wide")

# Custom CSS for styling
st.markdown(
    """
    <style>
    .header {
        text-align: center;
        font-size: 2em;
        color: #ff4b4b;
    }
    .intro {
        text-align: center;
        font-size: 1.2em;
        margin: 20px;
    }
    .sidebar {
        background-color: #f0f2f6;
        padding: 20px;
    }
    .content {
        padding: 20px;
    }
    .btn-primary {
        background-color: #ff4b4b;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar
st.sidebar.title("Olympic Insights")
st.sidebar.image('Olympic.jpeg', use_column_width=True)
user_menu = st.sidebar.radio(
    'Select an option',
    ('Welcome', 'Medal Tally', 'Overall Analysis', 'Country-wise Analysis', 'Athlete-wise Analysis')
)

# Page content based on user selection
if user_menu == 'Welcome':
    st.markdown("<h1 class='header'>Welcome to Olympic Insights</h1>", unsafe_allow_html=True)
    intro_text = """
    Explore 120 years of Olympic history through data! Dive into comprehensive analyses, visualizations, and insights that span the entire journey of the modern Olympic Games from 1896 to 2016. Whether you're a sports enthusiast, a data analyst, or simply curious about the Olympics, our app offers a rich and interactive experience to uncover the stories behind the medals, athletes, and nations.
    """
    st.markdown(f"<p class='intro'>{intro_text}</p>", unsafe_allow_html=True)
    st.image('Olympic.jpeg', use_column_width=True)

# Load data
df = pd.read_csv('athlete_events.csv')
region_df = pd.read_csv('noc_regions.csv')
df = preprocessor.preprocess(df, region_df)

# Medal Tally
if user_menu == 'Medal Tally':
    st.markdown("<h2 class='header'>Medal Tally</h2>", unsafe_allow_html=True)
    years, country = helper.country_year_list(df)

    selected_year = st.selectbox("Select Year", years)
    selected_country = st.selectbox("Select Country", country)

    medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)
    if selected_year == 'Overall' and selected_country == 'Overall':
        st.title("Overall Tally")
    if selected_year != 'Overall' and selected_country == 'Overall':
        st.title(f"Medal Tally in {selected_year} Olympics")
    if selected_year == 'Overall' and selected_country != 'Overall':
        st.title(f"{selected_country} Overall performance")
    if selected_year != 'Overall' and selected_country != 'Overall':
        st.title(f"{selected_country} performance in {selected_year} Olympics")
    st.table(medal_tally)

# Overall Analysis
if user_menu == 'Overall Analysis':
    st.markdown("<h2 class='header'>Overall Analysis</h2>", unsafe_allow_html=True)

    # Display key statistics
    editions = df['Year'].unique().shape[0] - 1
    cities = df['City'].unique().shape[0]
    sports = df['Sport'].unique().shape[0]
    events = df['Event'].unique().shape[0]
    athletes = df['Name'].unique().shape[0]
    nations = df['region'].unique().shape[0]

    st.title("Top Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Editions", editions)
    with col2:
        st.metric("Hosts", cities)
    with col3:
        st.metric("Sports", sports)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Events", events)
    with col2:
        st.metric("Nations", nations)
    with col3:
        st.metric("Athletes", athletes)

    # Plots
    nations_over_time = helper.data_over_time(df, 'region')
    fig = px.line(nations_over_time, x='Edition', y='region', title='Participating Nations Over the Years')
    st.plotly_chart(fig)

    events_over_time = helper.data_over_time(df, 'Event')
    fig = px.line(events_over_time, x='Edition', y='Event', title='Events Over the Years')
    st.plotly_chart(fig)

    athlete_over_time = helper.data_over_time(df, 'Name')
    fig = px.line(athlete_over_time, x='Edition', y='Name', title='Athletes Over the Years')
    st.plotly_chart(fig)

    st.title("No. of Events Over Time (Every Sport)")
    fig, ax = plt.subplots(figsize=(20, 20))
    x = df.drop_duplicates(['Year', 'Sport', 'Event'])
    sns.heatmap(x.pivot_table(index='Sport', columns='Year', values='Event', aggfunc='count').
                fillna(0).astype('int'), annot=True, cmap='YlGnBu')
    st.pyplot(fig)

    st.title("Most Successful Athletes")
    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, 'Overall')

    selected_sport = st.selectbox('Select a Sport', sport_list)
    x = helper.most_successful(df, selected_sport)
    st.table(x)

# Country-wise Analysis
if user_menu == 'Country-wise Analysis':
    st.markdown("<h2 class='header'>Country-wise Analysis</h2>", unsafe_allow_html=True)

    country_list = df['region'].dropna().unique().tolist()
    country_list.sort()

    selected_country = st.selectbox('Select a Country', country_list)

    country_df = helper.yearwise_medal_tally(df, selected_country)
    fig = px.line(country_df, x="Year", y="Medal", title=f"{selected_country} Medal Tally Over the Years")
    st.plotly_chart(fig)

    st.title(f"{selected_country} Excels in the Following Sports")
    pt = helper.country_event_heatmap(df, selected_country)
    fig, ax = plt.subplots(figsize=(20, 20))
    sns.heatmap(pt, annot=True, cmap='coolwarm')
    st.pyplot(fig)

    st.title(f"Top 10 Athletes of {selected_country}")
    top10_df = helper.most_successful_countrywise(df, selected_country)
    st.table(top10_df)

# Athlete-wise Analysis
if user_menu == 'Athlete-wise Analysis':
    st.markdown("<h2 class='header'>Athlete-wise Analysis</h2>", unsafe_allow_html=True)

    athlete_df = df.drop_duplicates(subset=['Name', 'region'])

    x1 = athlete_df['Age'].dropna()
    x2 = athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna()
    x3 = athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna()
    x4 = athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()

    fig = ff.create_distplot([x1, x2, x3, x4],
                             ['Overall Age', 'Gold Medalist', 'Silver Medalist', 'Bronze Medalist'],
                             show_hist=False, show_rug=False)
    fig.update_layout(autosize=False, width=1000, height=600)
    st.plotly_chart(fig)

    famous_sports = [
        'Basketball', 'Judo', 'Football', 'Tug of war', 'Athletics',
        'Swimming', 'Badminton', 'Sailing', 'Gymnastics',
        'Art Competitions', 'Handball', 'Weightlifting', 'Wrestling',
        'Water Polo', 'Hockey', 'Rowing', 'Fencing',
        'Shooting', 'Boxing', 'Taekwondo', 'Cycling', 'Diving', 'Canoeing',
        'Tennis', 'Golf', 'Softball', 'Archery',
        'Volleyball', 'Synchronized swimming', 'Table Tennis', 'Baseball',
        'Rhythmic Gymnastics', 'Rugby Sevens',
        'Beach Volleyball', 'Triathlon', 'Rugby', 'Polo', 'Ice Hockey'
    ]
    x = []
    name = []

    for sport in famous_sports:
        temp_df = athlete_df[athlete_df['Sport'] == sport]
        ages = temp_df[temp_df['Medal'] == 'Gold']['Age'].dropna().tolist()
        if ages:
            x.append(ages)
            name.append(sport)

    fig = ff.create_distplot(x, name, show_hist=False, show_rug=False)
    fig.update_layout(autosize=False, width=1000, height=600)
    st.plotly_chart(fig)

    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, 'Overall')

    selected_sport = st.selectbox('Select a Sport', sport_list)
    temp_df = helper.weight_v_heigth(df, selected_sport)
    fig, ax = plt.subplots()
    sns.scatterplot(x=temp_df['Weight'], y=temp_df['Height'], hue=temp_df['Medal'], style=temp_df['Sex'], s=60)
    st.pyplot(fig)

    st.title("Men vs Women Participation Over the Years")
    final = helper.men_vs_women(df)
    fig = px.line(final, x="Year", y=["Male", "Female"], title="Men vs Women Participation Over the Years")
    fig.update_layout(autosize=False, width=1000, height=600)
    st.plotly_chart(fig)
