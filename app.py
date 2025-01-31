import streamlit as st
import openai
import PyPDF2
import re
from io import BytesIO
from docx import Document
from googleapiclient.discovery import build

# YouTube API Key
API_KEY = "AIzaSyCHv8f7oqsfoTVBKSY60kbfYh8wacK9QDc"
youtube = build("youtube", "v3", developerKey=API_KEY)


def get_chatbot_response(messages, client):
    try:
        response = client.chat.completions.create(
            model="Meta-Llama-3.3-70B-Instruct",
            messages=messages,
            temperature=0.1,
            top_p=0.1,
            max_tokens = 4096
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


def extract_titles_and_contents(text):
    sections = re.split(r'(?m)^(?=[A-Z][^\n]*$)', text)
    structured_content = {}
    for section in sections:
        lines = section.strip().split("\n", 1)
        if len(lines) == 2:
            title, content = lines
            structured_content[title.strip()] = content.strip()
    return structured_content


def generate_word_doc(explanations):
    doc = Document()
    doc.add_heading("Detailed Explanations", level=1)
    for title, content in explanations.items():
        doc.add_heading(title, level=2)
        cleaned_content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
        cleaned_content = re.sub(r'\*(.*?)\*', r'\1', cleaned_content)
        cleaned_content = re.sub(r'__(.*?)__', r'\1', cleaned_content)
        cleaned_content = re.sub(r'_(.*?)_', r'\1', cleaned_content)
        doc.add_paragraph(cleaned_content)
    word_output = BytesIO()
    doc.save(word_output)
    word_output.seek(0)
    return word_output


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
        st.session_state.messages = [
            {"role": "system",
             "content": "You are a detailed and knowledgeable assistant. Provide thorough explanations."}
        ]

    st.sidebar.header("Input Fields")
    user_title = st.sidebar.text_input("Enter Title")
    uploaded_file = st.sidebar.file_uploader("Upload PDF", type=["pdf"])

    explanations = {}

    if uploaded_file is not None:
        extracted_text = extract_text_from_pdf(uploaded_file)
        structured_content = extract_titles_and_contents(extracted_text)

        for title, content in structured_content.items():
            user_prompt = f"""
                As an expert educator, generate **comprehensive and in-depth study material** on '{title}' based on the provided syllabus content. Ensure the material is detailed, well-structured, and engaging. The generated content should strictly align to the syllabus {extracted_text}.
                Do Day-wise Breakdown (For eg: In Day 1 this topic can be thought, in day 2 this topic can be thought)
                
                ### **Structure the Learning Material as Follows:**
            
                1. **Introduction:**  
                   - Provide a thorough overview of the topic.  
                   - Explain its significance and real-world relevance.  
            
                2. **Detailed Explanation of Key Concepts:**  
                   - Cover all fundamental and advanced concepts in depth.  
                   - Use step-by-step explanations, diagrams (if possible), and examples.  
                   - Include necessary formulas, algorithms, or theoretical frameworks.  
            
                3. **Real-World Applications & Case Studies:**  
                   - Describe how the concepts are used in real life.  
                   - Provide industry-specific examples and case studies.  
            
                4. **Step-by-Step Learning Path:**  
                   - Guide the learner through an optimal sequence for mastering the topic.  
                   - Include prerequisite knowledge and progression recommendations.  
            
                5. **Common Misconceptions & Pitfalls:**  
                   - Address frequently misunderstood aspects of the topic.  
                   - Clarify mistakes students often make.  
            
                6. **Advanced Insights & Future Trends:**  
                   - Explore emerging trends, advanced research, and industry applications.  
                   - Mention recent developments related to the topic.  
            
                7. **Summary & Key Takeaways:**  
                   - Highlight the most important points.  
                   - Reinforce learning with quick revision notes.  
                """
            st.session_state.messages.append({"role": "user", "content": user_prompt})
            bot_response = get_chatbot_response(st.session_state.messages, client)
            explanations[title] = bot_response
            st.session_state.messages.append({"role": "assistant", "content": bot_response})

    if user_title:
        user_prompt = f"Title: {user_title}\nProvide a detailed and thorough explanation."
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        bot_response = get_chatbot_response(st.session_state.messages, client)
        explanations[user_title] = bot_response
        st.session_state.messages.append({"role": "assistant", "content": bot_response})

    if explanations:
        for title, explanation in explanations.items():
            st.markdown(f"### {title}")
            st.write(explanation)
            st.write("\n")

        word_file = generate_word_doc(explanations)
        st.download_button(
            label="Download Explanations as Word Document",
            data=word_file,
            file_name="explanations.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        st.subheader("Recommended YouTube Videos 📺")
        with st.spinner("Fetching relevant YouTube videos..."):
            videos = search_videos(user_title if user_title else "AI learning")
            if videos:
                with st.expander(videos[0]["title"], expanded=False):
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
    else:
        st.write("No topics extracted or explained yet.")


if __name__ == "__main__":
    main()