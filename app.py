import streamlit as st
import os
import google.generativeai as genai
from prompts import content_brief_prompt

# --- Configuration ---
# Try to get the API key from Streamlit's secrets management first
try:
    # This is the preferred method for deployment
    api_key = st.secrets["GOOGLE_API_KEY"]
except (KeyError, AttributeError):
    # Fallback to environment variable for local development
    api_key = os.environ.get("GOOGLE_API_KEY")

# Configure the Gemini API if a key was found
if api_key:
    genai.configure(api_key=api_key)
else:
    st.error(
        "Google API Key not found. Please set it in your Streamlit secrets (`.streamlit/secrets.toml`) or as an environment variable."
    )
    st.stop()


# --- Functions ---
def generate_content_brief(
    topic, keywords, tone, word_count, page_type, user_intent
):
    """
    Generates a content brief using the Gemini API.

    Args:
        topic (str): The main topic/primary keyword.
        keywords (str): Supporting keywords, comma-separated.
        tone (str): The desired tone of voice.
        word_count (int): The requested word count.
        page_type (str): The type of page the content is for.
        user_intent (str): The primary user intent.

    Returns:
        str: The generated content brief or an error message.
    """
    if not topic:
        return "Error: Main Topic / Primary Keyword is a required field."

    try:
        model = genai.GenerativeModel("gemini-2.5-pro")
        prompt = content_brief_prompt.format(
            topic=topic,
            keywords=keywords,
            tone=tone,
            word_count=word_count,
            page_type=page_type,
            user_intent=user_intent,
        )
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred while generating the content brief: {e}"


# --- Streamlit App UI ---
st.set_page_config(page_title="Content Brief Generator", layout="wide")

st.title("📝 Briefium-Generatus")
st.markdown(
    "This tool helps you create a detailed content brief for your website using AI. Fill in the details below to generate your brief."
)

with st.sidebar:
    st.header("Configuration")
    st.info(
        """
        To deploy this app, set your Google API Key in Streamlit's secrets.
        Create a `.streamlit/secrets.toml` file with:
        ```toml
        GOOGLE_API_KEY = "YOUR_API_KEY_HERE"
        ```
        For local development, you can instead set an environment variable.
        Get your key from [Google AI Studio](https://aistudio.google.com/).
        """
    )


with st.form("brief_generator_form"):
    st.header("Content Details")

    # --- Input Fields ---
    main_topic = st.text_input(
        "**Main Topic / Primary Keyword** *",
        help="What is the core subject of your content? (e.g., 'benefits of content marketing')",
    )

    supporting_keywords = st.text_input(
        "**Supporting Keywords**",
        help="List any secondary keywords, comma-separated. (e.g., 'content strategy', 'SEO', 'brand awareness')",
    )

    col1, col2 = st.columns(2)
    with col1:
        tone_of_voice = st.selectbox(
            "**Tone of Voice**",
            [
                "",
                "Professional",
                "Casual", "Friendly",
                "Authoritative",
                "Witty",
                "Empathetic",
                "Technical",
            ],
            help="Select the desired tone for the content.",
        )
        page_type = st.selectbox(
            "**Page Type**",
            [
                "",
                "Blog Post / Article",
                "Landing Page",
                "Product Page",
                "Service Page",
                "Pillar Page",
                "Case Study",
            ],
            help="What kind of page is this content for?",
        )

    with col2:
        word_count = st.number_input(
            "**Requested Word Count**",
            min_value=300,
            max_value=5000,
            step=50,
            value=1500,
            help="Estimate the target length of the content.",
        )
        user_intent = st.selectbox(
            "**Primary User Intent**",
            [
                "",
                "Informational (Know)",
                "Navigational (Go)",
                "Transactional (Do)",
                "Commercial Investigation (Investigate)",
            ],
            help="What is the main reason a user is searching for this topic?",
        )

    submit_button = st.form_submit_button("Generate Content Brief", type="primary")


# --- Output Display ---
if submit_button:
    if not main_topic:
        st.error("The 'Main Topic / Primary Keyword' field is required.")
    else:
        with st.spinner("🧠 Generating your content brief... please wait."):
            generated_brief = generate_content_brief(
                main_topic,
                supporting_keywords,
                tone_of_voice,
                word_count,
                page_type,
                user_intent,
            )
        st.subheader("Generated Content Brief")
        st.markdown(generated_brief)
