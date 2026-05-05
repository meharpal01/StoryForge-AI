# import json
# import logging
# import os
# import sys
# from langchain_openai import ChatOpenAI
# from dotenv import load_dotenv

# # --- Initialization ---
# load_dotenv()
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# if not GROQ_API_KEY:
#     print("❌ Error: GROQ_API_KEY not found in .env file.")
#     sys.exit(1)

# llm = ChatOpenAI(
#     model="llama-3.3-70b-versatile",
#     api_key=GROQ_API_KEY,
#     base_url="https://api.groq.com/openai/v1",
#     temperature=0.7
# )

# VALID_ROLES = [
#     "Software Engineer", "Test Engineer", "Product Owner", 
#     "Scrum Master", "Architect", "DevOps Engineer", "QA Engineer"
# ]

# def generate_story(requirement, role, context=""):
#     """The Gen AI engine that builds the story with DoD and DoR."""
#     prompt = f"""
#     You are an expert Agile Business Analyst. 
#     Requirement: {requirement}
#     User Persona/Role: {role}
#     Additional Context: {context}

#     Return ONLY a JSON object with this structure:
#     {{
#         "ust_subject": "As a {role}, I want to... so that...",
#         "summary": "Detailed context and benefit",
#         "acceptance_criteria": ["Point 1", "Point 2"],
#         "definition_of_ready": ["Requirement 1", "Requirement 2"],
#         "definition_of_done": ["Criteria 1", "Criteria 2"],
#         "tasks": {{
#             "analysis": "Specific analysis task",
#             "implementation": "Core task",
#             "review": "Verification task"
#         }},
#         "checklists": {{
#             "self": ["Point 1", "Point 2"]
#         }}
#     }}
#     """
#     try:
#         response = llm.invoke(prompt)
#         content = response.content.strip()
#         if content.startswith("```"):
#             content = content.strip("```").replace("json", "", 1).strip()
#         return json.loads(content)
#     except Exception as e:
#         return {"error": str(e)}

# def main():
#     print("🚀 --- GenAI User Story Architect --- 🚀")
    
#     # Role Selection
#     print("\nSelect your role:")
#     for idx, r in enumerate(VALID_ROLES, 1):
#         print(f"{idx}. {r}")
    
#     role_input = input("\nEnter choice (number or name): ").strip()
#     selected_role = None
#     if role_input.isdigit() and 0 < int(role_input) <= len(VALID_ROLES):
#         selected_role = VALID_ROLES[int(role_input)-1]
#     else:
#         for r in VALID_ROLES:
#             if role_input.lower() == r.lower():
#                 selected_role = r
#                 break
    
#     if not selected_role: selected_role = "Team Member"
    
#     print(f"\n✅ Acting as: {selected_role}")
#     user_req = input("Requirement: ")
#     user_context = input("Extra context (e.g. Japan Bench): ")

#     print("\n✨ Architecting... please wait...")
#     current_story = generate_story(user_req, selected_role, user_context)

#     while True:
#         if "error" in current_story:
#             print(f"❌ Error: {current_story['error']}")
#             break

#         # --- UPDATED DISPLAY LOGIC ---
#         print("\n" + "═"*60)
#         print(f"TITLE: {current_story.get('ust_subject')}")
#         print("─"*60)
#         print(f"SUMMARY: {current_story.get('summary')}")
        
#         print("\n📋 DEFINITION OF READY (DoR):")
#         for item in current_story.get('definition_of_ready', []):
#             print(f"  ready? [ ] {item}")

#         print("\n✅ ACCEPTANCE CRITERIA:")
#         for ac in current_story.get('acceptance_criteria', []):
#             print(f"  check [ ] {ac}")

#         print("\n🏁 DEFINITION OF DONE (DoD):")
#         for item in current_story.get('definition_of_done', []):
#             print(f"  done? [ ] {item}")

#         print("\n🛠️ TASKS:")
#         tasks = current_story.get('tasks', {})
#         print(f"  - Analysis: {tasks.get('analysis')}")
#         print(f"  - Implementation: {tasks.get('implementation')}")
#         print(f"  - Review: {tasks.get('review')}")

#         print("═"*60)

#         refine = input("\nRefine this? (y/n) or 'exit': ").lower()
#         if refine == 'y':
#             feedback = input("Feedback: ")
#             current_story = generate_story(user_req, selected_role, f"Feedback: {feedback}. Previous: {json.dumps(current_story)}")
#         else:
#             break

# if __name__ == "__main__":
#     main()

import streamlit as st
import json
import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# --- Page Config ---
st.set_page_config(page_title="User Story Architect", page_icon="🚀", layout="wide")

# --- CSS for Beauty ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #FF4B4B; color: white; }
    .stDownloadButton>button { width: 100%; border-radius: 5px; }
    .status-box { padding: 20px; border-radius: 10px; background-color: white; border-left: 5px solid #FF4B4B; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- Initialization ---
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY not found in .env file.")
    st.stop()

llm = ChatOpenAI(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
    temperature=0.7
)

# --- AI Logic ---
def generate_story(requirement, role, context="", feedback=""):
    """Force AI to provide 4-5 points for DoD/DoR and handle refinement."""
    refinement_prompt = f"\nUser Feedback to incorporate: {feedback}" if feedback else ""
    
    prompt = f"""
    You are an expert Agile Business Analyst. 
    Requirement: {requirement}
    Persona: {role}
    Context: {context} {refinement_prompt}

    Return ONLY a JSON object.
    STRICT CONSTRAINTS:
    - acceptance_criteria: 4-5 items
    - definition_of_ready: 4-5 items 
    - definition_of_done: 4-5 items
    
    JSON Structure:
    {{
        "ust_subject": "As a {role}, I want to... so that...",
        "summary": "Detailed context",
        "acceptance_criteria": [],
        "definition_of_ready": [],
        "definition_of_done": [],
        "tasks": {{"analysis": "", "implementation": "", "review": ""}}
    }}
    """
    try:
        response = llm.invoke(prompt)
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
        return json.loads(content)
    except Exception as e:
        return {"error": str(e)}

# --- Streamlit UI ---
st.title("📋 StoryForge AI")
st.markdown("Craft professional Agile User Stories in seconds")

with st.sidebar:
    st.header("Settings")
    role = st.selectbox("Your Role", ["Software Engineer", "Test Engineer", "Product Owner", "Architect", "QA Engineer"])
    req = st.text_area("Requirement", placeholder="e.g. Implement XCP protocol validation")
    context = st.text_input("Extra Context", placeholder="e.g. Testing on Japan Bench")
    
    generate_btn = st.button("Generate User Story")

# State management for the story
if "story" not in st.session_state:
    st.session_state.story = None

if generate_btn and req:
    with st.spinner("Architecting..."):
        st.session_state.story = generate_story(req, role, context)

# Display Output
if st.session_state.story:
    if "error" in st.session_state.story:
        st.error(st.session_state.story["error"])
    else:
        story = st.session_state.story
        
        # Header Section
        st.subheader(f"📌 {story['ust_subject']}")
        st.info(story['summary'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📋 Definition of Ready (DoR)")
            for item in story['definition_of_ready']:
                st.write(f"⬜ {item}")
            
            st.markdown("### ✅ Acceptance Criteria")
            for item in story['acceptance_criteria']:
                st.write(f"🔹 {item}")

        with col2:
            st.markdown("### 🏁 Definition of Done (DoD)")
            for item in story['definition_of_done']:
                st.write(f"🚩 {item}")
            
            # st.markdown("### 🛠️ Development Tasks")
            # st.json(story['tasks'])
            st.markdown("### 🛠️ Development Tasks")
            tasks = story['tasks']
            st.write(f"🔍 **Analysis:** {tasks.get('analysis', '')}")
            st.write(f"⚙️ **Implementation:** {tasks.get('implementation', '')}")
            st.write(f"👁️ **Review:** {tasks.get('review', '')}")

        st.divider()
        
        # Refinement Section
        st.subheader("🔄 Refine this Story")
        feedback = st.text_input("What would you like to change?", key="feedback_input")
        if st.button("Update Story"):
            with st.spinner("Updating..."):
                st.session_state.story = generate_story(req, role, context, feedback)
                st.rerun()

        # Export Section
        st.download_button(
            label="Download as JSON",
            data=json.dumps(story, indent=4),
            file_name="user_story.json",
            mime="application/json"
        )