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

# ✅ Sidebar with Navigation
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4697/4697260.png", width=100)
    st.title("📘 Dashboard Menu")
    selection = st.radio("Go to Section:", [
        "📊 Ratings", "😬️ Sentiments", "☁️ WordClouds", "📋 Summary", "🗅️ Download"])
    st.markdown("---")
    st.info("👨‍💼 Contact Developer")
    st.markdown("""
- 📧 [zubairpatel128@gmail.com](mailto:zubairpatel128@gmail.com)  
- 🔗 [LinkedIn](https://www.linkedin.com/in/mohammed-zubair03)  
- 💻 [GitHub](https://github.com/mohdzubairpatel)
""", unsafe_allow_html=True)

# ✅ File Upload
st.title("📘 College Event Feedback Analysis Dashboard")
st.markdown("<small>If no file is uploaded, the default dataset will be used automatically.</small>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("📄 Upload your Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("✅ Using uploaded dataset.")
else:
    try:
        df = pd.read_excel("finalDataset0.2.xlsx")
        st.info("ℹ️ No file uploaded. Loaded default dataset: finalDataset0.2.xlsx")
    except FileNotFoundError:
        st.error("❌ No file uploaded and default dataset not found. Please upload an Excel file.")
        st.stop()

# ✅ Rename Columns
columns = [
    'Teaching_Rating', 'Teaching_Feedback',
    'CourseContent_Rating', 'CourseContent_Feedback',
    'Examination_Rating', 'Examination_Feedback',
    'Labwork_Rating', 'Labwork_Feedback',
    'Library_Rating', 'Library_Feedback',
    'Extracurricular_Rating', 'Extracurricular_Feedback']
df.columns = columns

# ✅ Normalize Ratings
rating_columns = [
    'Teaching_Rating', 'CourseContent_Rating', 'Examination_Rating',
    'Labwork_Rating', 'Library_Rating', 'Extracurricular_Rating']
rating_map = {-1: 1, 0: 3, 1: 5}
df[rating_columns] = df[rating_columns].apply(pd.to_numeric, errors='coerce').replace(rating_map)

# ✅ Sentiment Analysis
def get_sentiment(text):
    if pd.isnull(text): return 'Neutral'
    polarity = TextBlob(str(text)).sentiment.polarity
    return 'Positive' if polarity > 0.1 else 'Negative' if polarity < -0.1 else 'Neutral'

feedback_cols = [
    'Teaching_Feedback', 'Library_Feedback', 'Labwork_Feedback',
    'Extracurricular_Feedback', 'CourseContent_Feedback', 'Examination_Feedback']

for col in feedback_cols:
    df[col.replace('Feedback', 'Sentiment')] = df[col].apply(get_sentiment)

sentiment_cols = [col.replace('Feedback', 'Sentiment') for col in feedback_cols]

# ✅ Generate Summary Table
summary = pd.DataFrame({
    'Category': rating_columns,
    'Average Rating': df[rating_columns].mean().values,
    'Positive Feedback (%)': [
        100 * (df[col.replace('Rating', 'Sentiment')] == 'Positive').sum() / len(df)
        for col in rating_columns
    ]
})

# ✅ Navigation Routing
if selection == "📊 Ratings":
    st.header("📊 Rating Insights")
    avg_ratings = df[rating_columns].mean().sort_values().reset_index()
    avg_ratings.columns = ['Category', 'Average_Rating']
    fig1 = px.bar(
        avg_ratings, x='Average_Rating', y='Category', orientation='h',
        color='Category', text='Average_Rating',
        color_discrete_sequence=px.colors.qualitative.Vivid,
        title='Average Ratings Across Feedback Categories')
    fig1.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig1.update_layout(title_x=0.5, xaxis=dict(range=[0, 5]))
    st.plotly_chart(fig1, use_container_width=True)

elif selection == "😬️ Sentiments":
    st.header("😤 Sentiment Distribution by Category")
    col1, col2 = st.columns(2)
    for i, sentiment_col in enumerate(sentiment_cols):
        sentiment_counts = df[sentiment_col].value_counts()
        fig = go.Figure([
            go.Pie(
                labels=sentiment_counts.index,
                values=sentiment_counts.values,
                marker=dict(colors=['#98FB98', '#D3D3D3', '#FF6F61']),
                textinfo='percent+label', hole=0.3
            )
        ])
        fig.update_layout(title_text=f"{sentiment_col.replace('_', ' ')}", title_x=0.5, height=380)
        (col1 if i % 2 == 0 else col2).plotly_chart(fig, use_container_width=True)

elif selection == "☁️ WordClouds":
    st.header("☁️ Word Clouds")
    for col in feedback_cols:
        sentiment_col = col.replace('Feedback', 'Sentiment')
        col1, col2 = st.columns(2)
        for idx, (sentiment, color) in enumerate([('Positive', 'Greens'), ('Negative', 'Reds')]):
            text = ' '.join(df[df[sentiment_col] == sentiment][col].dropna().astype(str))
            if text.strip():
                wordcloud = WordCloud(width=600, height=400, background_color='white', colormap=color).generate(text)
                (col1 if idx == 0 else col2).markdown(f"**{col.replace('_', ' ')} - {sentiment}**")
                (col1 if idx == 0 else col2).image(wordcloud.to_array())

elif selection == "📋 Summary":
    st.header("📋 Summary Table & Satisfaction")
    st.dataframe(summary.style.background_gradient(cmap='YlGnBu'))

    df['Satisfaction_Level'] = df[rating_columns].mean(axis=1).apply(
        lambda x: 'High' if x > 4 else 'Medium' if x > 2.5 else 'Low'
    )
    st.subheader("🌟 Student Satisfaction Levels")
    st.bar_chart(df['Satisfaction_Level'].value_counts())

    all_sentiments = pd.concat([df[col] for col in sentiment_cols])
    sentiment_summary = all_sentiments.value_counts()
    fig = px.pie(
        names=sentiment_summary.index,
        values=sentiment_summary.values,
        title='Overall Sentiment Proportion in Feedback',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig.update_layout(title_x=0.5)
    st.plotly_chart(fig, use_container_width=True)

    pos_percent = [
        100 * (df[col.replace('Rating', 'Sentiment')] == 'Positive').sum() / len(df)
        for col in rating_columns
    ]
    fig = px.bar(
        x=rating_columns, y=pos_percent,
        labels={'x': 'Category', 'y': 'Positive Feedback (%)'},
        color=rating_columns, text=pos_percent,
        color_discrete_sequence=px.colors.qualitative.Dark2,
        title='Positive Feedback Percentage per Category'
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(title_x=0.5, yaxis_range=[0, 100])
    st.plotly_chart(fig, use_container_width=True)

elif selection == "🗅️ Download":
    st.header("🗅️ Download Cleaned Dataset & Summary")
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
