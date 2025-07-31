# 📘 College Feedback Analysis Interactive Dashboard (Streamlit UI Version)

# ✅ Step 1: Install Required Libraries (Run only once)
# !pip install streamlit pandas plotly openpyxl textblob wordcloud matplotlib seaborn xlsxwriter --quiet

# ✅ Step 2: Import Libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from textblob import TextBlob
import warnings
import io

warnings.filterwarnings('ignore')
sns.set(style='whitegrid')
st.set_page_config(layout="wide", page_title="College Feedback Dashboard", page_icon="📘")

# ✅ Step 3: Title and File Upload
with st.container(border=True):
    st.title("📘 College Event Feedback Analysis Dashboard")
    st.caption("Upload a student feedback Excel file below. If none is uploaded, a sample dataset will be used.")
    uploaded_file = st.file_uploader("📄 Upload your Excel file", type=["xlsx"])

# ✅ Step 4: Sidebar Menu with Navigation
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4697/4697260.png", width=120)
    st.markdown("## 📘 Dashboard Menu")
    st.markdown("**Navigate through the sections below:**")
    selected_tab = st.radio("### Go To Section", [
        "📊 Ratings",
        "🔊 Sentiments",
        "☁️ WordClouds",
        "📋 Summary",
        "📁 Download"
    ])
    st.markdown("---")
    st.markdown("### 👨‍💼 Contact Developer")
    st.markdown("""
- 📧 [zubairpatel128@gmail.com](mailto:zubairpatel128@gmail.com)  
- 🔗 [LinkedIn](https://www.linkedin.com/in/mohammed-zubair03)  
- 💻 [GitHub](https://github.com/mohdzubairpatel)
""", unsafe_allow_html=True)

# ✅ Step 5: Load Dataset
@st.cache_data
def load_data(file_path_or_buffer):
    return pd.read_excel(file_path_or_buffer)

if uploaded_file:
    df = load_data(uploaded_file)
    st.success("✅ Uploaded dataset loaded successfully.")
else:
    try:
        df = load_data("finalDataset0.2.xlsx")
        st.info("📂 Default dataset loaded: finalDataset0.2.xlsx")
    except FileNotFoundError:
        st.error("❌ Default dataset not found. Please upload a file.")
        st.stop()

# ✅ Step 6: Rename Columns
df.columns = [
    'Teaching_Rating', 'Teaching_Feedback',
    'CourseContent_Rating', 'CourseContent_Feedback',
    'Examination_Rating', 'Examination_Feedback',
    'Labwork_Rating', 'Labwork_Feedback',
    'Library_Rating', 'Library_Feedback',
    'Extracurricular_Rating', 'Extracurricular_Feedback'
]

# ✅ Step 7: Normalize Ratings
rating_columns = [
    'Teaching_Rating', 'CourseContent_Rating', 'Examination_Rating',
    'Labwork_Rating', 'Library_Rating', 'Extracurricular_Rating'
]
rating_map = {-1: 1, 0: 3, 1: 5}
df[rating_columns] = df[rating_columns].apply(pd.to_numeric, errors='coerce').replace(rating_map)

# ✅ Step 8: Sentiment Analysis
@st.cache_data
def analyze_sentiments(data, feedback_columns):
    def get_sentiment(text):
        if pd.isnull(text): return 'Neutral'
        polarity = TextBlob(str(text)).sentiment.polarity
        return 'Positive' if polarity > 0.1 else 'Negative' if polarity < -0.1 else 'Neutral'

    for col in feedback_columns:
        data[col.replace('Feedback', 'Sentiment')] = data[col].apply(get_sentiment)
    return data

feedback_cols = [
    'Teaching_Feedback', 'Library_Feedback', 'Labwork_Feedback',
    'Extracurricular_Feedback', 'CourseContent_Feedback', 'Examination_Feedback'
]

df = analyze_sentiments(df, feedback_cols)
sentiment_cols = [col.replace('Feedback', 'Sentiment') for col in feedback_cols]

# ✅ Step 9: Prepare Summary DataFrame
summary = pd.DataFrame({
    'Category': rating_columns,
    'Average Rating': df[rating_columns].mean().values,
    'Positive Feedback (%)': [
        100 * (df[col.replace('Rating', 'Sentiment')] == 'Positive').sum() / len(df)
        for col in rating_columns
    ]
})

# ✅ Step 10: Ratings Tab
if selected_tab == "📊 Ratings":
    with st.container(border=True):
        st.header("📊 Rating Insights")
        avg_ratings = df[rating_columns].mean().sort_values().reset_index()
        avg_ratings.columns = ['Category', 'Average_Rating']
        fig = px.bar(
            avg_ratings, x='Average_Rating', y='Category', orientation='h',
            color='Category', text='Average_Rating',
            color_discrete_sequence=px.colors.qualitative.Vivid
        )
        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig.update_layout(title='Average Ratings Across Feedback Categories', title_x=0.5, xaxis=dict(range=[0, 5]))
        st.plotly_chart(fig, use_container_width=True)

# ✅ Step 11: Sentiments Tab
elif selected_tab == "🔊 Sentiments":
    with st.container(border=True):
        st.header("🔊 Feedback Sentiment Distribution")
        col1, col2 = st.columns(2)
        for i, sentiment_col in enumerate(sentiment_cols):
            sentiment_counts = df[sentiment_col].value_counts()
            fig = go.Figure([go.Pie(labels=sentiment_counts.index, values=sentiment_counts.values, hole=0.3)])
            fig.update_layout(title_text=sentiment_col.replace('_', ' '), title_x=0.5, height=350)
            if i % 2 == 0:
                col1.plotly_chart(fig, use_container_width=True)
            else:
                col2.plotly_chart(fig, use_container_width=True)

# ✅ Step 12: WordClouds Tab 
elif selected_tab == "☁️ WordClouds":
    with st.container(border=True):
        st.header("☁️ Word Clouds of Feedback")

        @st.cache_data
        def generate_wordcloud(text, color):
            return WordCloud(width=600, height=400, background_color='white', colormap=color).generate(text)

        with st.expander("🔍 Click to View Word Clouds", expanded=False):
            for col in feedback_cols:
                sentiment_col = col.replace('Feedback', 'Sentiment')
                col1, col2 = st.columns(2)
                for idx, (sentiment, color) in enumerate([('Positive', 'Greens'), ('Negative', 'Reds')]):
                    text = ' '.join(df[df[sentiment_col] == sentiment][col].dropna().astype(str))[:1000]
                    if text.strip():
                        wc = generate_wordcloud(text, color)
                        if idx == 0:
                            col1.subheader(f"{col.replace('_', ' ')} - {sentiment}")
                            col1.image(wc.to_array())
                        else:
                            col2.subheader(f"{col.replace('_', ' ')} - {sentiment}")
                            col2.image(wc.to_array())

# ✅ Step 13: Summary Tab
elif selected_tab == "📋 Summary":
    with st.container(border=True):
        st.header("📋 Summary of Ratings and Sentiments")
        styled_summary = summary.style.format({
            "Average Rating": "{:.2f}",
            "Positive Feedback (%)": "{:.2f}"
        }).set_properties(**{'text-align': 'center'}).background_gradient(cmap='YlGnBu')
        st.dataframe(styled_summary)

        df['Satisfaction_Level'] = df[rating_columns].mean(axis=1).apply(
            lambda x: 'High' if x > 4 else 'Medium' if x > 2.5 else 'Low')
        st.subheader("🌟 Student Satisfaction Levels")
        st.bar_chart(df['Satisfaction_Level'].value_counts())

        all_sentiments = pd.concat([df[col] for col in sentiment_cols])
        sentiment_summary = all_sentiments.value_counts()
        fig = px.pie(names=sentiment_summary.index, values=sentiment_summary.values, hole=0.4)
        fig.update_layout(title='Overall Sentiment Distribution', title_x=0.5)
        st.plotly_chart(fig, use_container_width=True)

# ✅ Step 14: Download Tab
elif selected_tab == "📁 Download":
    with st.container(border=True):
        st.header("📁 Download Cleaned Dataset & Summary")
        st.markdown("This file includes cleaned feedback data and summarized rating and sentiment analysis.")
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Cleaned_Data')
            summary.to_excel(writer, index=False, sheet_name='Summary')
        st.download_button(
            label="📄 Download Excel Report",
            data=output.getvalue(),
            file_name="College_Feedback_Summary.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
