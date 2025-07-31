# 📘 College Feedback Analysis Interactive Dashboard (Interactive Sidebar Navigation)

# ✅ Step 1: Install Required Libraries (Run once)
# !pip install streamlit pandas plotly openpyxl textblob wordcloud matplotlib seaborn xlsxwriter --quiet

# ✅ Step 2: Import Libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from textblob import TextBlob
import warnings
import io

warnings.filterwarnings('ignore')
sns.set(style='whitegrid')

# ✅ Set Page Config
st.set_page_config(layout="wide", page_title="College Feedback Dashboard", page_icon="📘")

# ✅ Sidebar Navigation
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4697/4697260.png", width=100)
    st.title("📘 Dashboard Menu")
    page = st.radio("Go to:", [
        "📊 Ratings", "😬️ Sentiments", "☁️ WordClouds", "📋 Summary", "🗅️ Download"
    ])
    st.markdown("---")
    st.info("👨‍💻 Developed by Mohammed Zubair")
    st.markdown("""
    📧 [Email](mailto:zubairpatel128@gmail.com)  
    🔗 [LinkedIn](https://www.linkedin.com/in/mohammed-zubair03)  
    💻 [GitHub](https://github.com/mohdzubairpatel)
    """, unsafe_allow_html=True)

# ✅ Title & File Upload
st.title("📘 College Event Feedback Analysis Dashboard")
st.markdown("<small>If no file is uploaded, a default dataset will be loaded automatically.</small>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📄 Upload Excel Feedback File", type=["xlsx"])

# ✅ Load Data
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("✅ File uploaded successfully!")
else:
    try:
        df = pd.read_excel("finalDataset0.2.xlsx")
        st.info("ℹ️ No file uploaded. Using default dataset.")
    except FileNotFoundError:
        st.error("❌ Default dataset not found. Please upload a file to proceed.")
        st.stop()

# ✅ Rename Columns
df.columns = [
    'Teaching_Rating', 'Teaching_Feedback',
    'CourseContent_Rating', 'CourseContent_Feedback',
    'Examination_Rating', 'Examination_Feedback',
    'Labwork_Rating', 'Labwork_Feedback',
    'Library_Rating', 'Library_Feedback',
    'Extracurricular_Rating', 'Extracurricular_Feedback'
]

# ✅ Normalize Ratings
rating_columns = [
    'Teaching_Rating', 'CourseContent_Rating', 'Examination_Rating',
    'Labwork_Rating', 'Library_Rating', 'Extracurricular_Rating'
]
rating_map = {-1: 1, 0: 3, 1: 5}
df[rating_columns] = df[rating_columns].apply(pd.to_numeric, errors='coerce').replace(rating_map)

# ✅ Sentiment Analysis
def get_sentiment(text):
    if pd.isnull(text): return 'Neutral'
    polarity = TextBlob(str(text)).sentiment.polarity
    return 'Positive' if polarity > 0.1 else 'Negative' if polarity < -0.1 else 'Neutral'

feedback_cols = [
    'Teaching_Feedback', 'Library_Feedback', 'Labwork_Feedback',
    'Extracurricular_Feedback', 'CourseContent_Feedback', 'Examination_Feedback'
]

for col in feedback_cols:
    df[col.replace('Feedback', 'Sentiment')] = df[col].apply(get_sentiment)

sentiment_cols = [col.replace('Feedback', 'Sentiment') for col in feedback_cols]

# ✅ Ratings Page
if page == "📊 Ratings":
    st.header("📊 Average Ratings per Category")
    avg_ratings = df[rating_columns].mean().sort_values().reset_index()
    avg_ratings.columns = ['Category', 'Average Rating']
    fig1 = px.bar(avg_ratings, x='Average Rating', y='Category', orientation='h',
                  color='Category', text='Average Rating',
                  color_discrete_sequence=px.colors.qualitative.Vivid)
    fig1.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig1.update_layout(title_x=0.5, xaxis=dict(range=[0, 5]))
    st.plotly_chart(fig1, use_container_width=True)

# ✅ Sentiments Page
elif page == "😬️ Sentiments":
    st.header("😬 Sentiment Analysis by Category")
    col1, col2 = st.columns(2)
    for i, sentiment_col in enumerate(sentiment_cols):
        sentiment_counts = df[sentiment_col].value_counts()
        fig = go.Figure([go.Pie(labels=sentiment_counts.index, values=sentiment_counts.values,
                                marker=dict(colors=['#90EE90', '#D3D3D3', '#FF6F61']),
                                textinfo='percent+label', hole=0.3)])
        fig.update_layout(title_text=sentiment_col.replace('_', ' '), title_x=0.5, height=360)
        (col1 if i % 2 == 0 else col2).plotly_chart(fig, use_container_width=True)

# ✅ WordClouds Page
elif page == "☁️ WordClouds":
    st.header("☁️ Feedback Word Clouds")
    for col in feedback_cols:
        sentiment_col = col.replace('Feedback', 'Sentiment')
        col1, col2 = st.columns(2)
        for sentiment, color, target_col in [('Positive', 'Greens', col1), ('Negative', 'Reds', col2)]:
            text = ' '.join(df[df[sentiment_col] == sentiment][col].dropna().astype(str))
            if text.strip():
                wc = WordCloud(width=600, height=400, background_color='white', colormap=color).generate(text)
                target_col.markdown(f"**{col.replace('_', ' ')} - {sentiment}**")
                target_col.image(wc.to_array())

# ✅ Summary Page
elif page == "📋 Summary":
    st.header("📋 Summary Overview")
    summary_df = pd.DataFrame({
        'Category': rating_columns,
        'Average Rating': df[rating_columns].mean().values,
        'Positive Feedback (%)': [
            100 * (df[col.replace('Rating', 'Sentiment')] == 'Positive').sum() / len(df)
            for col in rating_columns
        ]
    })
    st.dataframe(summary_df.style.background_gradient(cmap='YlGnBu'))

    st.subheader("🌟 Student Satisfaction Levels")
    df['Satisfaction_Level'] = df[rating_columns].mean(axis=1).apply(
        lambda x: 'High' if x > 4 else 'Medium' if x > 2.5 else 'Low'
    )
    st.bar_chart(df['Satisfaction_Level'].value_counts())

    all_sentiments = pd.concat([df[col] for col in sentiment_cols])
    fig = px.pie(names=all_sentiments.value_counts().index,
                 values=all_sentiments.value_counts().values,
                 title="Overall Sentiment Proportion",
                 hole=0.4, color_discrete_sequence=px.colors.qualitative.Safe)
    fig.update_layout(title_x=0.5)
    st.plotly_chart(fig, use_container_width=True)

# ✅ Download Page
elif page == "🗅️ Download":
    st.header("🗅️ Download Cleaned Data & Summary")
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Cleaned_Data')
        summary_df.to_excel(writer, index=False, sheet_name='Summary')

    st.download_button(
        label="📄 Download Excel Report",
        data=output.getvalue(),
        file_name="College_Feedback_Summary.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
