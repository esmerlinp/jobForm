import streamlit as st
from datetime import datetime
import pdfplumber
import json

def leer_pdf(file_obj) -> str:
    texto = ""
    with pdfplumber.open(file_obj) as pdf:
        for pagina in pdf.pages:
            texto += pagina.extract_text() + "\n"
    return texto



def leer_pdf_from_path(path):
    texto = ""
    with pdfplumber.open(path) as pdf:
        for pagina in pdf.pages:
            texto += pagina.extract_text() + "\n"
    return texto


# Función para renderizar los campos dentro de un contenedor
def render_custom_fields_in_container(fields, requeridos=False):
    print(fields)
    fields = sorted(fields, key=lambda x: x['order'])  # Ordenar por el campo "order"
    form_data = {}
    
    container = st.container()  # Crear un contenedor
    with container:
        for field in fields:
            required = field.get("required", False)
            if requeridos:
                if not required:
                    continue
       
            
            fieldName =  field.get("fieldName")
            field_type = field.get("typename", "")
            label = field.get("label")
            value = field.get("value", "")
            placeholder = field.get("placeHolder", "")
            options = field.get("options", [])
            

            if field_type == "text_input":
                form_data[field["fieldName"]] = st.text_input(
                    key= fieldName,
                    label=label,
                    value=value if value else None,
                    placeholder=placeholder,
                    help="Este campo es requerido" if required else None
                )
            elif field_type == "text_area":
                form_data[field["fieldName"]] = st.text_area(
                    key= fieldName,
                    label=label,
                    value=value if value else None,
                    placeholder=placeholder,
                    help="Este campo es requerido" if required else None
                )
            elif field_type == "number_input":
                form_data[field["fieldName"]] = st.number_input(
                    key= fieldName,
                    label=label,
                    value=value if value else 0,
                    step=1,
                    placeholder=placeholder,
                    help="Este campo es requerido" if required else None
                )
            elif field_type == "select":
                opc = [x['value'] for x in options]
                print(opc)
                form_data[field["fieldName"]] = st.selectbox(
                    key= fieldName,
                    label=label,
                    options=opc,
                    index=opc.index(value) if value in opc else 0,
                    help="Este campo es requerido" if required else None,
                )
            elif field_type == "select_multiple":
                opc = [x['value'] for x in options]
                print(opc)
                form_data[field["fieldName"]] = st.multiselect(
                    key= fieldName,
                    label=label,
                    options=opc,
                    help="Este campo es requerido" if required else None,
                )
            elif field_type == "date":
                form_data[field["fieldName"]] = st.text_input(
                    key= fieldName,
                    label=label,
                    value= datetime.today().strftime("%d-%m-%Y"),
                    placeholder="dd-mm-yyyy ej. 31-12-2025",
                    help="Este campo es requerido" if required else None,
                )
                
        st.session_state.customFields = json.dumps(form_data)
       
    return container