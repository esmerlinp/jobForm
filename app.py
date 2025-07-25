import streamlit as st
from app.core.api_jobs import fetch_jobs_offers
import streamlit_antd_components as sac
from app.pages.job_detail import job_detail
import pandas as pd
from streamlit_extras.row import row

st.set_page_config(
    page_title="Job Details",
    page_icon=":briefcase:",
    layout="wide",
)

job_id = st.query_params.get("job_id", None)
company_id = st.query_params.get("comp", 6)
cliente_id = st.query_params.get("client", "rrhh")

#http://localhost:8501/?job_id=1089&comp=6
    
grados_academicos = [
        "Todos",
        "1-Secundaria",
        "2-Bachillerato",
        "3-Técnico",
        "4-Licenciatura",
        "5-Maestría",
        "6-Doctorado",
]
  
if job_id:
    
    with st.spinner():
        job = fetch_jobs_offers(job_id=job_id, company_id=company_id)
    
    job_detail(job, company_id)
else:

    #with st.spinner():
    jobs = fetch_jobs_offers(company_id=company_id)
    
    def callback():
        st.write("Texto ingresado:", st.session_state.mi_input)
    
    if jobs is not None:
        
        if not "detail_index" in st.session_state:
             st.session_state.detail_index = 0
             
        _, col_filters, _ = st.columns([1,3,1])
        
        with col_filters:
            
            row2 = row([2, 2, 2, 2, 4], vertical_align="bottom")
            row2.selectbox("Salario", ["Todos", "Italy", "Japan", "USA"])
            row2.selectbox("Modalidad", ["Todos", "Remota", "Presencial", "Hibrida"])
            row2.selectbox("Tipo Contrato", ["Todos", "Fijo", "Temporal", "Freelancer"])
            row2.selectbox("Nivel Academico", grados_academicos)
            row2.text_input("Buscar", icon=":material/search:", placeholder="Buscar por posición o palabra clave", label_visibility="collapsed",  key="mi_input", on_change=callback)
           

                    
        st.divider()

        _, col_list,_, col_detail, _ = st.columns([0.7,2,0.5,3,0.7])
        
        with col_list:
            st.subheader("Ofertas de Empleo")
            for i, job in enumerate(jobs):
                with st.container(border=True):
                    st.markdown(f"##### {job.job_title}")
                    st.empty()
                    st.markdown(f"###### {job.company_name}")
                    #st.caption(f"América Latina · {job.workMode} · {job.contract_type_name} · {job.salary} DOP$/Mes")
                    
                    

                    sac.tags([
                        sac.Tag(label='América Latina', icon='geo-alt-fill', color="blue"),
                        sac.Tag(label=job.workMode, icon='house', color="orange"),
                        sac.Tag(label=job.contract_type_name, icon='briefcase-fill', color="geekblue"),
                        sac.Tag(label=job.salary if job.salary else "No definido", icon='cash-coin'),
                    ], align='start', key=f"{i}tags")
   
                    st.write(job.job_description.capitalize())
                        
                    if st.button("Ver mas detalle", key=i):
                        st.session_state.detail_index = i
                     
                
        with col_detail: 
            job_detail(jobs[st.session_state.detail_index], company_id)                           
    else:
        st.write("No hay ofertas de empleos")
            
    st.stop()