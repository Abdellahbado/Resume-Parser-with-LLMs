from utils import parse_resume
import streamlit as st
import os
from dotenv import load_dotenv
from models import ResumeData


def main():
    st.set_page_config(page_title="Resume Parser", page_icon="📄", layout="wide")

    st.title("📄 Resume Parser")
    st.write("Upload a PDF resume (regular or scanned) to extract key information.")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        with st.spinner("Parsing resume..."):

            with open("temp.pdf", "wb") as f:
                f.write(uploaded_file.getbuffer())

            resume_data = parse_resume("temp.pdf")

            os.remove("temp.pdf")

        col1, col2 = st.columns(2)

        with col1:
            st.header("Personal Information")
            if resume_data.full_name:
                st.subheader(resume_data.full_name)
            else:
                st.subheader("Name not found")

            if resume_data.contact_information:
                if resume_data.contact_information.email:
                    st.write(f"📧 Email: {resume_data.contact_information.email}")
                if resume_data.contact_information.phone_number:
                    st.write(
                        f"📞 Phone: {resume_data.contact_information.phone_number}"
                    )
                if resume_data.contact_information.address:
                    st.write(f"🏠 Address: {resume_data.contact_information.address}")
            else:
                st.write("No valid contact information found.")

            if resume_data.skills:
                st.subheader("Skills")
                skills = resume_data.skills
                initial_display = 5
                if len(skills) > initial_display:
                    with st.expander("Display all skills"):
                        for skill in skills:
                            st.write(f"- {skill}")
                else:
                    for skill in skills:
                        st.write(f"- {skill}")

            if resume_data.languages:
                st.subheader("Languages")
                for language in resume_data.languages:
                    if language.name:
                        lang_info = language.name
                        if language.proficiency:
                            lang_info += f" - {language.proficiency}"
                        st.write(f"- {lang_info}")
                        if language.certifications:
                            with st.expander("Certifications"):
                                if isinstance(language.certifications, list):
                                    for cert in language.certifications:
                                        st.write(f"  • {cert}")
                                else:
                                    st.write(f"  • {language.certifications}")
        with col2:
            if resume_data.contact_information:
                st.header("Professional Links")
                contact_info = resume_data.contact_information
                if contact_info.linkedin:
                    st.markdown(f"[LinkedIn]({contact_info.linkedin})")
                if contact_info.personal_website:
                    st.markdown(f"[Personal Website]({contact_info.personal_website})")
                if contact_info.github:
                    st.markdown(f"[GitHub]({contact_info.github})")

            if resume_data.education:
                st.subheader("Education")
                for edu in resume_data.education:
                    edu_title = edu.degree or edu.institution or "Education Entry"
                    if edu.degree and edu.institution:
                        edu_title = f"{edu.degree} from {edu.institution}"
                    with st.expander(edu_title):
                        if edu.city:
                            st.write(f"**Location:** {edu.city}")
                        if edu.graduation_date:
                            st.write(f"**Graduation Date:** {edu.graduation_date}")
                        if edu.gpa and edu.gpa != "N/A":
                            st.write(f"**GPA:** {edu.gpa}")
                        if edu.achievements:
                            st.write("**Achievements:**")
                            if isinstance(edu.achievements, list):
                                for achievement in edu.achievements:
                                    st.write(f"- {achievement}")
                            else:
                                st.write(f"- {edu.achievements}")

            if resume_data.work_experience:
                st.subheader("Work Experience")
                for experience in resume_data.work_experience:
                    exp_title = experience.company or "Unknown Company"
                    if experience.position:
                        exp_title = f"{experience.position} at {exp_title}"
                    with st.expander(exp_title):
                        if experience.start_date:
                            end_date = experience.end_date or "Present"
                            st.write(
                                f"**Duration:** {experience.start_date} - {end_date}"
                            )
                        if experience.responsibilities:
                            st.write("**Responsibilities:**")
                            for resp in experience.responsibilities:
                                st.write(f"- {resp}")


if __name__ == "__main__":
    load_dotenv()
    main()
