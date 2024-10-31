import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter

def fetch_stats(selected_user, df):
    """Fetch overall statistics for the selected user."""
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    num_messages = df.shape[0]
    words = df['message'].str.split(expand=True).stack().count()
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]
    num_links = df[df['message'].str.contains('http')].shape[0]

    return num_messages, words, num_media_messages, num_links

def monthly_timeline(selected_user, df):
    """Create a monthly timeline of messages."""
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    timeline['time'] = timeline['month'] + "-" + timeline['year'].astype(str)
    return timeline

def daily_timeline(selected_user, df):
    """Create a daily timeline of messages."""
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('date').count()['message'].reset_index()
    return daily_timeline

def week_activity_map(selected_user, df):
    """Get the most busy day of the week."""
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user, df):
    """Get the most busy month."""
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user, df):
    """Generate a heatmap of user activity."""
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)
    return user_heatmap

def most_busy_users(df):
    """Get the most busy users in the chat."""
    x = df['user'].value_counts().head()
    new_df = df['user'].value_counts().reset_index()
    new_df.columns = ['user', 'messages']
    return x, new_df

def create_wordcloud(selected_user, df, exclude_words):
    """Generate a word cloud image from messages."""
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    def remove_stop_words(message):
        combined_exclude = [word.strip().lower() for word in exclude_words if word.strip() != '']
        return " ".join(word for word in message.lower().split() if word not in combined_exclude)

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    temp['message'] = temp['message'].apply(remove_stop_words)
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc

def most_common_words(selected_user, df, exclude_words):
    """Get the most common words used in messages."""
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    words = []
    for message in temp['message']:
        for word in message.lower().split():
            if word not in exclude_words:  # Check against exclude_words
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df

def emoji_helper(selected_user, df):
    """Analyze the emojis used in the chat."""
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([char for char in message if char in emoji.UNICODE_EMOJI['en']])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    return emoji_df
