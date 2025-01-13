import streamlit as st
import os
import pandas as pd
import time
import requests
import base64

# Configuración de la página
st.set_page_config(page_title="Ofertas de Empleo", layout="wide")
global df_ofertas
df_ofertas = pd.DataFrame()


relative_path = './logo.png' 
full_path = os.path.join(os.getcwd(), relative_path)
path = os.path.abspath(full_path)


_, col2, _= st.columns([0.3, 1, 0.3])
# with col1:
#     st.image(f"{path}", width=100)
    

    
@st.cache_data(ttl=60*60)
def get_jobs():
    return pd.read_json("./sample.json")
    baseUrl = "http://rrhh.administracionapi.camsoft.com.do:8086"
    x_api_key = "AJEFTSLBSUXBTIILJPQKSNNXTETCMFRRWHQSLIHBDJQVBFELRO"
    
    #baseUrl = os.getenv("RRHH_BASE_URL")
    #x_api_key = os.getenv("RRHH_API_KEY")
    url = f"{baseUrl}/ApiGateway/api/v1/requisitions/"
    
    x_ui_culture = "es-DO"
    headers = {
        "Content-type": "application/json",
        "x-api-key": x_api_key,
        "x-ui-culture": x_ui_culture
    }
    print(headers, url)
    response = requests.get(url=url, headers=headers)
    
    if response.status_code == 200:
        result = response.json()["result"]
        return pd.DataFrame(result)
    else:
        print(response.text)
        return None
    


# Definir el estado de la sesión para la navegación
if "page" not in st.session_state:
    st.session_state.page = "home"  # Página inicial
    

if "jobid" in st.query_params and st.session_state.page != "form":
    st.session_state.jobRequisitionId = st.query_params.jobid
    st.session_state.page = "detail"
    

# if "jobRequisitionId" not in st.session_state:
#     st.session_state.jobRequisitionId = 0  # Página inicial
    


    
# Función para cambiar de página
def switch_page(page_name):
    st.session_state.page = page_name


# Función para convertir el archivo subido a Base64
def file_to_base64(file):
    return base64.b64encode(file.read()).decode("utf-8")
   
def send_request(data):
    baseUrl = os.getenv("RRHH_BASE_URL")
    x_api_key = os.getenv("RRHH_API_KEY")
    
    baseUrl = "http://rrhh.administracionapi.camsoft.com.do:8086"
    x_api_key = "AJEFTSLBSUXBTIILJPQKSNNXTETCMFRRWHQSLIHBDJQVBFELRO"
    
    url = f"{baseUrl}/ApiGateway/api/v1/applications/"
    x_ui_culture = "es-DO"
    

    
    headers = {
        "Content-type": "application/json",
        "x-api-key": x_api_key,
        "x-ui-culture": x_ui_culture
    }
    
    
    response = requests.post(url=url, headers=headers, json=data)
    if response.status_code == 201:
        return True    
    else:
        response.text
        return False    
        

with col2:
    # Navegación basada en el estado de la sesión
    if st.session_state.page == "home":
        st.title("Ofertas de Empleo")
        df_ofertas = get_jobs() 
        
        if df_ofertas is not None:
            
            colf, colf2, _= st.columns([1, 1, 0.3])
            
            # Filtro por ubicación
            ubicaciones = ["Todos"] + df_ofertas["companyName"].unique().tolist()
            with colf:
                filtro_ubicacion = st.selectbox("Filtrar por Empresa", ubicaciones)

                # Filtrar las ofertas
                if filtro_ubicacion != "Todos":
                    df_ofertas = df_ofertas[df_ofertas["companyName"] == filtro_ubicacion]



            # Filtro por departamento
            departmentName = ["Todos"] + df_ofertas["departmentName"].unique().tolist()
            with colf2:
                filtro_departmentName = st.selectbox("Filtrar por departamento", departmentName)

                # Filtrar las ofertas
                if filtro_departmentName != "Todos":
                    df_ofertas = df_ofertas[df_ofertas["departmentName"] == filtro_departmentName]
                
  
           
            # Mostrar las ofertas
            for h, oferta in df_ofertas.iterrows():
                container = st.container(border=True, key=h)
                with container:
                    colt, _, colbutton= st.columns([1, 1.1, 0.2])
                    with colt:
                        st.markdown(f"##### {oferta['jobTitle']}")

                        
                    with colbutton:
                        if st.button(key=f"{h}2{oferta['id']}", label=":blue[Aplicar]", type="tertiary"):
                            st.session_state.jobRequisitionId = oferta['id']
                            st.query_params.jobid = oferta['id']
                            switch_page("detail")
                            st.rerun()
                            
                    # st.write(f"**Empresa:** {oferta['companyName']}")
                    # st.write(f"**Descripción:** {oferta['description']}")
                    # st.write("**Responsabilidades**")
                    # st.markdown(oferta['responsibilities'])
                    # st.write()
                    # st.write("**Requisitos**")
                    # st.markdown(oferta['requirements'])

                    
                    
            
        else:
            st.write("No hay ofertas de empleos")
            
    elif st.session_state.page == "detail":
        col, _, _ = st.columns([0.5, 1.1, 0.2])
        with col:
            if st.button(":blue[< Atrás]", type="tertiary"):
                st.query_params.clear()
                switch_page("home")
                st.rerun()
                
                
        df = get_jobs()
        job = df[df["id"] == int(st.session_state.jobRequisitionId)]
        if not job.empty:
            st.title(job["jobTitle"].values[0])
            st.subheader(f"**Empresa:** {job['companyName'].values[0]}")
            st.write(f"**Descripción**")
            st.write(job['description'].values[0])

            st.write("**Responsabilidades**")
            st.markdown(job['responsibilities'].values[0])
            st.write()
            st.write("**Requisitos**")
            st.markdown(job['requirements'].values[0])

            if st.button(label=":red[Aplicar a Vacante]"):
                st.session_state.jobRequisitionId = job['id'].values[0]
                switch_page("form")
                st.rerun()

            st.write("---") 
        else:
            st.query_params.clear()
            switch_page("home")
            st.rerun()
            
    elif st.session_state.page == "form":
        
        df = get_jobs() 
        df = df[df["id"] == int(st.session_state.jobRequisitionId)]
        if st.button(":blue[< Atrás]", type="tertiary"):
            switch_page("detail")  
            st.rerun()
        st.subheader(df["jobTitle"].values[0])
        #st.markdown(f"**Empresa:** {df['companyName'].values[0]}")
        #st.write(f"**Descripción:** {df['description'].values[0]}")
        
        paises = (
                    "1-Republica Dominicana",
                    "2-Estados Unidos",
                    "3-México",
                    "4-Colombia",
                    "5-Venezuela",
                    "6-Argentina",
                    "7-Chile",
                    "8-Perú",
                    "9-Brasil",
                    "10-Cuba",
                    "11-Canadá",
                    "12-España",
                    "13-Francia",
                    "14-Alemania",
                    "15-Italia",
                    "16-Inglaterra",
                    "17-Japón",
                    "18-China",
                    "19-Corea del Sur",
                    "20-Haití"
                )
        nacionalidades = (
                    "1-Dominicana",
                    "2-Estadounidense",
                    "3-Mexicana",
                    "4-Colombiana",
                    "5-Venezolana",
                    "6-Argentina",
                    "7-Chilena",
                    "8-Peruana",
                    "9-Brasileña",
                    "10-Cubana",
                    "11-Canadiense",
                    "12-Española",
                    "13-Francesa",
                    "14-Alemana",
                    "15-Italiana",
                    "16-Inglesa",
                    "17-Japonesa",
                    "18-China",
                    "19-Coreana",
                    "20-Haitiana"
                )

        grados_academicos = (
            "1-Secundaria",
            "2-Bachillerato",
            "3-Técnico",
            "4-Licenciatura",
            "5-Maestría",
            "6-Doctorado",
        )
        
        # Botón para volver a la página principal
        
            
        with st.form("my_form"):
        
            # Información Personal
            st.caption("Información Personal")
            f, m = st.columns(2)
            l, s = st.columns(2)
            
            firstName = f.text_input(":red[*] Primer Nombre", placeholder="ej. Jhon")
            middleName = m.text_input("Segundo Nombre", placeholder="ej. Alexander")
            lastName = l.text_input(":red[*] Primer Apellido", placeholder="ej. Doe")
            surname = s.text_input("Segundo Apellido", placeholder="ej. Smith")
            
            gender = st.selectbox(":red[*] Género", ("1-Masculino", "2-Femenino"))
            birthDate = st.date_input(":red[*] Fecha de Nacimiento")
            maritalStatus = st.selectbox("Estado Civil", ("Soltero", "Casado", "Unión Libre"))

            # Identificación
            st.caption("Identificación")
            identificationType = st.selectbox("Tipo de identificación", ("1-Cédula", "5-Pasaporte"))
            identificationNumber = st.text_input(":red[*] Número de Identificación", placeholder="ej. 00100013305")

            # Lugar de Nacimiento y Nacionalidad
            st.caption("Lugar de Nacimiento y Nacionalidad")
            birthCountry = st.selectbox("Lugar de Nacimiento", paises)
            nationality = st.selectbox(":red[*] Nacionalidad", nacionalidades)

            # Educación
            st.caption("Educación")
            educationLevelId = st.selectbox(":red[*] Nivel Educativo", grados_academicos)
            experience = st.selectbox(":red[*]¿Cuántos años de experiencia profesional tienes en tu campo de especialización? (Cuenta solo las experiencias postuniversitarias, remuneradas a tiempo completo. Por favor, excluya las pasantías, los puestos a tiempo parcial o los proyectos académicos.)", ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10+"))
            degrees = st.text_area(label="Por favor, enumere su título universitario y su institución. En caso de que sea seleccionado para el puesto, tenga en cuenta que una oferta de trabajo dependerá de la confirmación de esta información a través de una verificación de antecedentes.", placeholder="Enter")
            # Residencia
            
            st.caption("Residencia")
            residenceCountry = st.selectbox(":red[*] ¿En qué país te encuentras?", paises)
            residenceCity = st.text_input(":red[*] ¿En qué ciudad te encuentras? (Por favor, añada también Estado/Provincia cuando corresponda)", placeholder="Enter")
            mobilePhone = st.text_input(":red[*] Teléfono Celular", placeholder="ej. 18090009999")
            email = st.text_input("Correo Electrónico", placeholder="ej. ejemplo@correo.com")
            linkedInUrl = st.text_input("LinkedIn URL*", placeholder="Enter")
            uploaded_file = st.file_uploader(":red[*] Resume/CV", type=['doc', 'pdf', 'docx', "png", "jpg", "txt", "bmp"])


            currentCompany = st.text_input(label=":red[*] Empresa actual", placeholder="Enter")
            currentSalary = st.number_input(
                label="Salario actual",
                min_value=0.0,  # Valor mínimo
                max_value=1_000_000.0,  # Valor máximo
                step=0.01,  # Incremento de los valores
                format="%.2f"  # Formato para mostrar dos decimales
            )
            desiredSalary = st.number_input(
                label="Salario deseado",
                min_value=0.0,  # Valor mínimo
                max_value=1_000_000.0,  # Valor máximo
                step=0.01,  # Incremento de los valores
                format="%.2f"  # Formato para mostrar dos decimales
            )
            compromise = st.selectbox(":red[*] ¿Cuándo puedes empezar? *", ('Inmediatamente', '1 Semana', '2 Semanas', '3 Semanas', '4 Semanas', '5 Semanas', '6 Semanas', '7 Semanas', '8 Semanas', '9 Semanas', '10 Semanas'))
            additionalInfo = st.text_area(label="Información adicional (añade una carta de presentación o cualquier otra cosa que quieras compartir)", placeholder="Enter")
           


            # Every form must have a submit button.
            submitted = st.form_submit_button("Submit")
            if submitted:
                
                customData = {
                    "gender": gender.split("-")[1],
                    "maritalStatus": maritalStatus,
                    "nationality": nationality.split("-")[1],
                    "residenceCountry": residenceCountry.split("-")[1],
                    "residenceCity": residenceCity,
                    "experience": experience,
                    "degrees": degrees,
                    "linkedInUrl": linkedInUrl,
                    "currentCompany": currentCompany,
                    "currentSalary": currentSalary,
                    "desiredSalary": desiredSalary,
                    "birthCountry": birthCountry.split("-")[1],
                    "additionalInfo":additionalInfo,
                    "compromise": compromise
                }
                data = {
                    "jobRequisitionId": int(st.session_state.jobRequisitionId),
                    "identificationType": int(identificationType.split("-")[0]),
                    "identificationNumber": identificationNumber,
                    "firstName": firstName.capitalize(),
                    "middleName": middleName.capitalize(),
                    "lastName": lastName.capitalize(),
                    "surname": surname.capitalize(),
                    "educationLevelId": int(educationLevelId.split("-")[0]),
                    "mobilePhone": mobilePhone,
                    "attachedDocument": None,
                    "fileExtension": "",
                    "maritalStatus": maritalStatus,
                    "gender": gender.split("-")[1],
                    "nationality": nationality.split("-")[1],
                    "birthDate": birthDate.strftime("%Y-%m-%d"),
                    "birthCountry": birthCountry.split("-")[1],
                    "email": email,
                    "residenceCountry": residenceCountry.split("-")[1],
                    "residenceCity": residenceCity,
                    "customData": customData
                }
                
                # Campos requeridos con nombres descriptivos
                required_fields = {
                    "jobRequisitionId": "Job Requisition ID",
                    "identificationType": "Identification Type",
                    "identificationNumber": "Número de Identificación",
                    "firstName": "Primer Nombre",
                    "lastName": "Segundo Nombre",
                    "educationLevelId": "Nivel Educativo",
                    "mobilePhone": "📱 Teléfono Celular",
                    "gender": "Genero",
                    "nationality": "Nacionalidad",
                    "birthDate": "Fecha de Nacimiento",
                    "birthCountry": "País de Nacimiento",
                    "email": "Correo Electrónico",
                    "residenceCountry": "País de Residencia",
                    "residenceCity": "Ciudad de Resicencia",
                    "maritalStatus": "Estado Civil",
                    "attachedDocument": "Resumen CV"
                }
                
                if uploaded_file is not None:
                    
                    # Convertir archivo a base64
                    file_base64 = file_to_base64(uploaded_file)
                    data["attachedDocument"] = file_base64
                    data["fileExtension"] = uploaded_file.type.split("/")[1]
                    
                
                
                # Validación de campos requeridos
                error = None
                for field, field_name in required_fields.items():
                    value = data.get(field)
                    if value is None or (isinstance(value, str) and not value.strip()):
                        error = f"{field_name} es requerido."
                        break
                
                if error:
                    st.error(error)  
                else:
                    msg = st.toast('Enviando...')
                    
                   
                    if send_request(data):
                        msg.toast('Solicitud enviada exitosamente...', icon="✅")
                        time.sleep(3)
                        st.session_state.page = "home"
                        st.rerun()
                    else:
                        msg.toast('Se presentó un error al envíar la solicitud. Por favor intente de nuevo.!', icon = "😰")
                        time.sleep(1)
                        st.error("Se presentó un error al envíar la solicitud. Por favor intente de nuevo.")
                        
            


