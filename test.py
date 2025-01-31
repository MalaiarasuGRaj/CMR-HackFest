import streamlit as st
import openai
import PyPDF2
import docx
from googleapiclient.discovery import build
from prompt_template import get_study_material_prompt

# YouTube API Key
API_KEY = "AIzaSyCHv8f7oqsfoTVBKSY60kbfYh8wacK9QDc"

# YouTube API service
youtube = build("youtube", "v3", developerKey=API_KEY)


def get_chatbot_response(messages, client):
    try:
        response = client.chat.completions.create(
            model='Meta-Llama-3.3-70B-Instruct',
            messages=messages,
            temperature=0.7,
            top_p=0.9,
            max_tokens=4096
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"


def extract_text_from_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text


def extract_text_from_docx(uploaded_file):
    doc = docx.Document(uploaded_file)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text


def extract_text(uploaded_file):
    if uploaded_file.name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif uploaded_file.name.endswith(".docx"):
        return extract_text_from_docx(uploaded_file)
    else:
        return "Unsupported file format. Please upload a PDF or Word (.docx) file."


def search_videos(content):
    search_query = f"What is {content}"
    search_response = youtube.search().list(
        q=search_query,
        part="snippet",
        type="video",
        maxResults=5
    ).execute()

    videos = []
    for item in search_response["items"]:
        videos.append({
            "title": item["snippet"]["title"],
            "description": item["snippet"]["description"],
            "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
            "video_id": item["id"]["videoId"]
        })
    return videos


def main():
    st.set_page_config(page_title="NVidya", layout="wide")
    st.markdown("<h1 style='text-align: center; color: yellow;'>NVidya - Your Intelligent Learning Partner</h1>",
                unsafe_allow_html=True)

    api_key = "e146e13e-46f6-4d38-8b67-a120c374803b"
    client = openai.OpenAI(
        api_key=api_key,
        base_url="https://api.sambanova.ai/v1",
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "generated_content" not in st.session_state:
        st.session_state.generated_content = None

    st.sidebar.header("Input Fields")
    topic = st.sidebar.text_input("Enter Topic (Required)", "")

    if not topic:
        st.sidebar.error("Topic is required!")

    uploaded_file = st.sidebar.file_uploader("Upload PDF or Word (.docx) (Optional)", type=["pdf", "docx"])
    extracted_text = ""

    if uploaded_file is not None:
        extracted_text = extract_text(uploaded_file)

    if st.sidebar.button("Generate") and topic:
        prompt = get_study_material_prompt(topic, extracted_text)

        st.session_state.messages = [
            {"role": "system",
             "content": "You are an AI assistant specializing in creating highly detailed and structured educational materials. Ensure clarity, accuracy, and depth in the content. Use appropriate formatting (headings, bullet points, numbered lists, and examples) for readability."},
            {"role": "user", "content": prompt}
        ]
        bot_response = get_chatbot_response(st.session_state.messages, client)
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        st.session_state.generated_content = bot_response

    if st.session_state.generated_content:
        st.subheader("Generated Study Material 📚")
        st.write(st.session_state.generated_content)

        with st.spinner("Fetching relevant YouTube videos..."):
            videos = search_videos(topic)
            if videos:
                st.subheader("Recommended YouTube Videos 📺")

                with st.expander(videos[0]["title"], expanded=True):
                    first_video = videos[0]
                    st.image(first_video["thumbnail"], width=200)
                    st.markdown(
                        f"**[{first_video['title']}](https://www.youtube.com/watch?v={first_video['video_id']})**")
                    st.write(first_video["description"])

                for video in videos[1:]:
                    with st.expander(video["title"]):
                        st.image(video["thumbnail"], width=200)
                        st.markdown(f"**[{video['title']}](https://www.youtube.com/watch?v={video['video_id']})**")
                        st.write(video["description"])
            else:
                st.error("No related videos found for the given topic.")


if __name__ == "__main__":
    main()