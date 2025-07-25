import streamlit as st



st.set_page_config(
    page_title="Job Details",
    page_icon=":briefcase:",
    layout="centered",
)

job_id = st.query_params.get("job_id", None)
company_id = st.query_params.get("comp", 0)
cliente_id = st.query_params.get("client", "rrhh")

#http://localhost:8501/?job_id=1089&comp=6
    

if job_id:
    from app.pages.job_detail import job_detail
    job_detail(job_id, company_id)
else:
    st.title("No job ID provided. Please check the URL.")
    st.stop()