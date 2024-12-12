import praw
import os
import streamlit as st
import time

# Set up Reddit client (ensure to replace with your own credentials)
# Reddit app credentials (update these with your new details)
reddit = praw.Reddit(
    client_id='Your client ID',  # Your client ID
    client_secret='Your secret',  # Your secret
    user_agent='automated_social:v1.0 (by u/Puzzled-Path9768)',  # Your user agent
    username='Reddit username',  # Your Reddit username
    password='Reddit password'  # Your Reddit password
)


# Function to post text on Reddit
def post_text(subreddit_name, title, body):
    try:
        subreddit = reddit.subreddit(subreddit_name)
        submission = subreddit.submit(title, selftext=body)
        st.success(f"Text post created in r/{subreddit_name} with title: '{title}' (ID: {submission.id})")
        return submission.id  # Return submission ID for later use
    except Exception as e:
        st.error(f"Failed to post text: {e}")

# Function to post an image on Reddit
def post_image(subreddit_name, title, image_path):
    try:
        subreddit = reddit.subreddit(subreddit_name)
        submission = subreddit.submit_image(title, image_path)
        st.success(f"Image post created in r/{subreddit_name} with title: '{title}' (ID: {submission.id})")
        return submission.id  # Return submission ID for later use
    except Exception as e:
        st.error(f"Failed to post image: {e}")

# Function to post a video on Reddit
def post_video(subreddit_name, title, video_path):
    try:
        subreddit = reddit.subreddit(subreddit_name)
        submission = subreddit.submit_video(title, video_path)
        st.success(f"Video post created in r/{subreddit_name} with title: '{title}' (ID: {submission.id})")
        return submission.id  # Return submission ID for later use
    except Exception as e:
        st.error(f"Failed to post video: {e}")

# Function to read recent posts from a subreddit
def read_recent_posts(subreddit_name, limit=5):
    try:
        subreddit = reddit.subreddit(subreddit_name)
        st.subheader(f"Recent posts from r/{subreddit_name}:")
        for submission in subreddit.new(limit=limit):
            st.write(f"Title: {submission.title} (ID: {submission.id})")
    except Exception as e:
        st.error(f"Failed to read posts: {e}")

# Function to delete a post from Reddit
def delete_post(post_id):
    try:
        submission = reddit.submission(id=post_id)
        submission.delete()
        st.success(f"Deleted post with ID: {post_id}")
    except Exception as e:
        st.error(f"Failed to delete post: {e}")

# Streamlit UI for Reddit operations
def main():
    st.title("Reddit Automation App")
    subreddit_name = st.text_input("Enter the subreddit name (e.g., 'test'):")

    if subreddit_name:
        option = st.selectbox(
            "Choose an operation:",
            ["Create Text Post", "Create Image Post", "Create Video Post", "Read Recent Posts", "Delete Post"]
        )

        if option == "Create Text Post":
            title = st.text_input("Enter the post title:")
            body = st.text_area("Enter the post body:")
            if st.button("Post Text"):
                if title and body:
                    post_text(subreddit_name, title, body)

        elif option == "Create Image Post":
            title = st.text_input("Enter the image post title:")
            image_path = st.text_input("Enter the path to the image file:")
            if st.button("Post Image"):
                if os.path.isfile(image_path):
                    post_image(subreddit_name, title, image_path)
                else:
                    st.error("Invalid image path. Please try again.")

        elif option == "Create Video Post":
            title = st.text_input("Enter the video post title:")
            video_path = st.text_input("Enter the path to the video file:")
            if st.button("Post Video"):
                if os.path.isfile(video_path):
                    post_video(subreddit_name, title, video_path)
                else:
                    st.error("Invalid video path. Please try again.")

        elif option == "Read Recent Posts":
            if st.button("Read Posts"):
                read_recent_posts(subreddit_name)

        elif option == "Delete Post":
            post_id = st.text_input("Enter the post ID to delete:")
            if st.button("Delete Post"):
                if post_id:
                    delete_post(post_id)

if __name__ == "__main__":
    main()

