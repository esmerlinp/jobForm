import streamlit as st
import json
from openai import OpenAI
import time
from app.util import render_custom_fields_in_container, leer_pdf
from app.core.api_jobs import apply_job_offert

client = OpenAI(api_key=st.secrets["openai_api_key"])  # or set OPENAI_API_KEY in your environment


customFields = []

                        
prompt= """Con los datos de este texto:

Si la información proporcionada **no corresponde claramente a un currículum vitae (hoja de vida)**, genera exclusivamente el siguiente diccionario JSON:
{"error": "La información proporcionada no corresponde a una hoja de vida"}

Si la información **sí corresponde a un currículum vitae**, genera un diccionario JSON que siga estrictamente esta estructura de claves sin modificarlas:

{
    "tipo_Identificacion": null,
    "identificacion": null,
    "id_Compania": null,
    "primer_Nombre": "",
    "segundo_Nombre": "",
    "primer_Apellido": "",
    "segundo_Apellido": "",
    "nombre_Completo": "",
    "comentario": "",
    "email": "",
    "telefono": "",
    "etiqueta": "",
    "id_GradoAcademico: ""
}

Llena los valores con los datos que correspondan del currículum (por ejemplo, nombre, teléfono, correo). Para el campo "etiqueta" agrega alguna cualidad destacada del solicitante basada en su perfil profesional. En el campo "comentario" incluye una valoración breve y objetiva del solicitante basada en la información del currículum y los datos del puesto a aplicar, coloca un :) si la valoracion es positiva y una :( sino es asi. No cambies las claves ni agregues nuevas. Si algún dato no está disponible, deja el valor como null.
Para tipo_Identificacion (numerico entero) poner valor entero 1 si identificacion es cédula, 2 si es pasaporte, y null si identificacion está vacío o es nulo
Para el campo id_GradoAcademico elige de los sigrientes valores enteros   1 para Secundaria, 2 Bachillerato, 3 Técnico, 4 Licenciatura, 5 para Maestría , 6 para Doctorado .
**La respuesta debe contener únicamente el diccionario JSON solicitado, sin sugerencias, explicaciones ni datos adicionales.**
"""


grados_academicos = (
        "1-Secundaria",
        "2-Bachillerato",
        "3-Técnico",
        "4-Licenciatura",
        "5-Maestría",
        "6-Doctorado",
    )
    
def preguntar_al_modelo(texto, prompt_usuario, job):
    respuesta = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Eres un asistente útil que analiza documentos."},
            {"role": "user", "content": f"{prompt_usuario}\n\nContenido del documento:\n{texto}\n\n Requisitos del empleo:{job}"}
        ]
    )
    return respuesta.choices[0].message.content





def generate_response(some_long_response):
    for line in some_long_response:
        yield line
        time.sleep(0.01)  # Optional delay for effect
        
        
        
        
@st.dialog("Aplicar al empleo", width="large")
def apply_job(job, company_id):
    """
    Function to handle job application logic.
    This function would typically interact with an API to submit the job application.
    """
    
    st.subheader("Aplicar al empleo")
    st.write("Adjunta tu CV para que gestionemos tu postulación al empleo de forma automática.")
    
    respuesta_dict = {}
    if not "cv_loaded" in st.session_state:
        st.session_state.cv_loaded = False
        
        
    if not "payload" in st.session_state:
        st.session_state.payload = {}
        

    uploaded_file = st.file_uploader(f"Adjuntar cv ", type=['pdf'], accept_multiple_files=False)
    
  
    
    if uploaded_file is not None:
       
        
        if not st.session_state.payload:
            texto_extraido = leer_pdf(uploaded_file)
            
            if not st.session_state.cv_loaded:
                with st.spinner("Procesando el CV..."):
                    respuesta = preguntar_al_modelo(texto_extraido, prompt, job)
                    
                    #convertir la respuesta a un diccionario
                    st.session_state.payload = json.loads(respuesta)
                    
                    if not isinstance(respuesta_dict, dict):
                        st.warning("Hubo un error al procesar el CV. Por favor, asegúrate de que el archivo sea un currículum vitae válido.")
                        return
                    
            
        if "error" in st.session_state.payload:
            st.write_stream(generate_response(st.session_state.payload["error"]))
            st.session_state.cv_loaded = False
        else:
            
            #validar los campos del dict que son null y solicitarlos al usuario
            st.caption("Campos obligatorios que faltan en tu CV")
            for key in st.session_state.payload.keys():
               
                if st.session_state.payload[key] is None or st.session_state.payload[key] == "":
                    if key == "tipo_Identificacion":
                        st.session_state.payload[key] = int(st.selectbox("Tipo de identificación", ("1-Cédula", "5-Pasaporte")).split("-")[0])
                    elif key == "id_GradoAcademico":
                        st.session_state.payload[key] = st.selectbox(":red[*] Nivel Educativo", grados_academicos)
                    else:
                        if not key in ["segundo_Nombre", "segundo_Apellido", "etiqueta", "id_Compania", "nombre_Completo", "nombre_Supervisor", "nombre_Departamento", "id_Departamento", "id_Requisicion"]:
                            st.session_state.payload[key] = st.text_input(f"Ingrese el valor para {key}:", value=st.session_state.payload[key])
            
            if "customData" in job:
                if job["customData"]:
                    strdata = str(job["customData"])
                    customFields= json.loads(strdata)
            
                    if customFields:    
                        container = render_custom_fields_in_container(customFields, requeridos=False)     
            
            if "customData" in job:
                if job["customData"]:
                    strdata = str(job["customData"])
                    customFields= json.loads(strdata)
                    print(customFields)
           
            
                
            with st.chat_message("ai"):
                st.markdown("### Valoración:")
                if not st.session_state.cv_loaded:
                    st.write_stream(generate_response(st.session_state.payload['comentario']))
                else:
                    st.write(st.session_state.payload['comentario'])
                    
            st.session_state.cv_loaded = True
            
                
                


            
   

    if st.button(f"Enviar solicitud"):
        
        for i, field in enumerate(customFields):
            ssession_data = json.loads(st.session_state.customFields)
            if field['fieldName'] in ssession_data:
                customFields[i]["value"] = ssession_data[field['fieldName']]
                
        st.session_state.payload["id_Requisicion"] = job["id"]
        st.session_state.payload["id_Compania"] = int(company_id)
        st.session_state.payload["id_Departamento"] = job["department_id"]
        st.session_state.payload["nombre_Departamento"] = job["department_name"]
        st.session_state.payload["nombre_Supervisor"] = job["supervisor_name"]
        st.session_state.payload["customData"] = json.dumps(customFields)
            
        

        
        st.json(st.session_state.payload)
        response = apply_job_offert(data=st.session_state.payload)
        if response.get("error"):
            st.error("No se pudo crear la solicitud")
        else:
            st.success("Solicitud enviada correctamente.")
        
        # data = json.dumps(customFields)
        # for item in data:
        #    val = item["value"]
        #    st.write(item)

                
                
                