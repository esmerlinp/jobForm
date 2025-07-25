import streamlit as st
from app.core.api_jobs import fetch_jobs_offers
import streamlit_antd_components as sac
from app.pages.job_detail import job_detail
import requests
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
    jobs_original = fetch_jobs_offers(company_id=company_id)
    
    if not "jobs" in st.session_state:
        st.session_state.jobs = jobs_original
   
    
    # def callback():
    #     if len(job.job_title) > 0:
    #         #st.session_state.jobs = [job for job in jobs_original if st.session_state.mi_input.lower() in job.job_title.lower() or st.session_state.mi_input.lower() in job.requirements.lower()]
    #         st.session_state.jobs = [
    #                                     job for job in jobs_original 
    #                                     if (
    #                                         (job.job_title and st.session_state.mi_input.lower() in job.job_title.lower()) or
    #                                         (job.requirements and st.session_state.mi_input.lower() in job.requirements.lower())
    #                                     )
    #                                 ]
    #         st.session_state.detail_index = 0
    #     else:
    #         st.session_state.jobs = jobs_original
        
    #     if st.session_state.filter_modalidad != "Todos":
    #         print("sdf")
    
    
    
    def callback():
        # Obtenemos el filtro de texto, lo pasamos a minúsculas para búsqueda case-insensitive
        filtro_texto = st.session_state.mi_input.lower() if st.session_state.mi_input else ""
        filtro_modalidad = st.session_state.get("filter_modalidad", "Todos")
        filtro_tipo_contrato = st.session_state.get("filter_tipo_contrato", "Todos")  # si tienes esa key
        filtro_nivel_academico = st.session_state.get("filter_nivel_academico", "Todos")
        
        # Aplicar filtros combinados sobre jobs_original
        filtered_jobs = []
        for job in jobs_original:
            # Filtrar por texto (job_title o requirements)
            texto_valido = (
                (job.job_title and filtro_texto in job.job_title.lower()) or
                (job.requirements and filtro_texto in job.requirements.lower())
            ) if filtro_texto else True
            
            # Filtrar por modalidad
            modalidad_valida = (filtro_modalidad == "Todos") or (job.workMode == filtro_modalidad)
            
            # Filtrar por tipo de contrato
            tipo_contrato_valido = (filtro_tipo_contrato == "Todos") or (job.contract_type_name == filtro_tipo_contrato)
            
            # Filtrar por nivel académico
            nivel_academico_valido = (filtro_nivel_academico == "Todos") or (job.nivel_academico == filtro_nivel_academico)
            
            # Si cumple todos los filtros, lo agregamos
            if texto_valido and modalidad_valida and tipo_contrato_valido and nivel_academico_valido:
                filtered_jobs.append(job)
                
        st.session_state.jobs = filtered_jobs
        # Reiniciar índice detalle para evitar errores IndexError
        st.session_state.detail_index = 0

    
    
    
    
    if st.session_state.jobs is not None:
        
        if not "detail_index" in st.session_state:
             st.session_state.detail_index = 0
             
        _, col_filters, _ = st.columns([1,3,1])
        
        with col_filters:
            
            row2 = row([2, 2, 2, 4], vertical_align="bottom")
            row2.selectbox("Compañía", ["Todos", "CCia-Prueba-6"], on_change=callback)
            row2.selectbox("Modalidad", ["Todos", "Remoto", "Presencial", "Híbrido"], key="filter_modalidad", on_change=callback)
            row2.selectbox("Tipo Contrato", ["Todos", "Fijo", "Temporal"], key="filter_tipo_contrato", on_change=callback)
            #row2.selectbox("Nivel Academico", grados_academicos, key="filter_nivel_academico",  on_change=callback)
            row2.text_input("Buscar", icon=":material/search:", placeholder="Buscar por posición o palabra clave", label_visibility="collapsed",  key="mi_input", on_change=callback)
      
            
                    
        st.divider()

        _, col_list,_, col_detail, _ = st.columns([0.7,2,0.5,3,0.7])
        
        with col_list:
            st.subheader("Ofertas de Empleo")
            for i, job in enumerate(st.session_state.jobs):
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
            if st.session_state.jobs:
                job_detail(st.session_state.jobs[st.session_state.detail_index], company_id) 
            else:
                 st.write("No hay ofertas de empleos")                          
    else:
        st.write("No hay ofertas de empleos")
            
    st.stop()