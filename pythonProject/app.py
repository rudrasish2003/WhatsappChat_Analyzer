import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

st.sidebar.title("WhatsApp Chat Analyzer")

# Upload chat file
uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    try:
        # Read and decode file
        bytes_data = uploaded_file.getvalue()
        data = bytes_data.decode("utf-8")
        
        # Preprocess data
        df = preprocessor.preprocess(data)

        # Fetch unique users
        user_list = df['user'].unique().tolist()
        if 'group_notification' in user_list:
            user_list.remove('group_notification')
        user_list.sort()
        user_list.insert(0, "Overall")

        # User selection
        selected_user = st.sidebar.selectbox("Show analysis with respect to", user_list)

        # Date filter
        st.sidebar.title("Select Date Range")
        start_date = st.sidebar.date_input("Start date", min(df['date']), min(df['date']))
        end_date = st.sidebar.date_input("End date", max(df['date']), max(df['date']))

        # Custom words to exclude
        st.sidebar.title("Exclude Words")
        exclude_words = st.sidebar.text_area("Enter words to exclude (comma-separated)", "").split(',')

        # Clean up exclude_words to remove any whitespace
        exclude_words = [word.strip().lower() for word in exclude_words if word.strip()]

        # Filter DataFrame by date range
        if start_date <= end_date:
            df = df[(df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))]
        else:
            st.sidebar.error("End date should be greater than or equal to the start date.")

        if st.sidebar.button("Show Analysis"):
            # Stats Area
            num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
            st.title("Top Statistics")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.header("Total Messages")
                st.title(num_messages)
            with col2:
                st.header("Total Words")
                st.title(words)
            with col3:
                st.header("Media Shared")
                st.title(num_media_messages)
            with col4:
                st.header("Links Shared")
                st.title(num_links)

            # Monthly timeline
            st.title("Monthly Timeline")
            timeline = helper.monthly_timeline(selected_user, df)
            fig, ax = plt.subplots()
            ax.plot(timeline['time'], timeline['message'], color='green')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

            # Daily timeline
            st.title("Daily Timeline")
            daily_timeline = helper.daily_timeline(selected_user, df)
            fig, ax = plt.subplots()
            ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

            # Activity map
            st.title('Activity Map')
            col1, col2 = st.columns(2)

            with col1:
                st.header("Most Busy Day")
                busy_day = helper.week_activity_map(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(busy_day.index, busy_day.values, color='purple')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            with col2:
                st.header("Most Busy Month")
                busy_month = helper.month_activity_map(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(busy_month.index, busy_month.values, color='orange')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            # Weekly activity map
            st.title("Weekly Activity Map")
            user_heatmap = helper.activity_heatmap(selected_user, df)
            fig, ax = plt.subplots()
            ax = sns.heatmap(user_heatmap, cmap="coolwarm")
            st.pyplot(fig)

            # Most busy users (Group level)
            if selected_user == 'Overall':
                st.title('Most Busy Users')
                x, new_df = helper.most_busy_users(df)
                fig, ax = plt.subplots()

                col1, col2 = st.columns(2)

                with col1:
                    ax.bar(x.index, x.values, color='red')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)
                with col2:
                    st.dataframe(new_df)

            # WordCloud
            st.title("Wordcloud")
            df_wc = helper.create_wordcloud(selected_user, df, exclude_words)
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            st.pyplot(fig)

            # Most common words
            most_common_df = helper.most_common_words(selected_user, df, exclude_words)
            fig, ax = plt.subplots()
            ax.barh(most_common_df[0], most_common_df[1])
            plt.xticks(rotation='vertical')

            st.title('Most Common Words')
            st.pyplot(fig)

            # Emoji analysis
            emoji_df = helper.emoji_helper(selected_user, df)
            st.title("Emoji Analysis")

            col1, col2 = st.columns(2)

            with col1:
                st.dataframe(emoji_df)
            with col2:
                fig, ax = plt.subplots()
                ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f")
                st.pyplot(fig)

    except UnicodeDecodeError:
        st.error("There was an error decoding the file. Please ensure it's a UTF-8 encoded text file.")
else:
    st.info("Please upload a WhatsApp chat file in UTF-8 format for analysis.")
