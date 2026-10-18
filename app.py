import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Calculadora de Edad Física", page_icon="🏃", layout="centered")

# --- ALGORITMO Y BAREMOS ---
BAREMOS = [
    {"edad": 20, "flexiones": 45, "dominadas": 15, "sentadillas": 50, "carrera_seg": 22 * 60},
    {"edad": 25, "flexiones": 40, "dominadas": 13, "sentadillas": 46, "carrera_seg": 23.5 * 60},
    {"edad": 30, "flexiones": 35, "dominadas": 11, "sentadillas": 42, "carrera_seg": 25 * 60},
    {"edad": 35, "flexiones": 30, "dominadas": 9,  "sentadillas": 38, "carrera_seg": 26.5 * 60},
    {"edad": 40, "flexiones": 25, "dominadas": 7,  "sentadillas": 34, "carrera_seg": 28 * 60},
    {"edad": 45, "flexiones": 20, "dominadas": 5,  "sentadillas": 30, "carrera_seg": 30 * 60},
    {"edad": 50, "flexiones": 15, "dominadas": 4,  "sentadillas": 26, "carrera_seg": 32 * 60},
    {"edad": 55, "flexiones": 11, "dominadas": 2,  "sentadillas": 22, "carrera_seg": 34.5 * 60},
    {"edad": 60, "flexiones": 8,  "dominadas": 1,  "sentadillas": 18, "carrera_seg": 37 * 60},
    {"edad": 65, "flexiones": 0,  "dominadas": 0,  "sentadillas": 0,  "carrera_seg": 45 * 60},
]

def interpolar_edad_prueba(valor, clave, es_inverso=False):
    limite_mejor = BAREMOS[0][clave]
    if (not es_inverso and valor >= limite_mejor) or (es_inverso and valor <= limite_mejor):
        return 20.0

    limite_peor = BAREMOS[-1][clave]
    if (not es_inverso and valor <= limite_peor) or (es_inverso and valor >= limite_peor):
        return 65.0

    for i in range(len(BAREMOS) - 1):
        b1, b2 = BAREMOS[i], BAREMOS[i + 1]
        v1, v2 = b1[clave], b2[clave]

        esta_en_rango = (valor <= v1 and valor >= v2) if not es_inverso else (valor >= v1 and valor <= v2)

        if esta_en_rango:
            # Evitar división por cero si v1 == v2
            if v1 == v2:
                return float(b1["edad"])
            fraccion = (valor - v1) / (v2 - v1)
            return b1["edad"] + fraccion * (b2["edad"] - b1["edad"])
    return 65.0

def obtener_zona_color(desfase):
    if desfase >= 10:
        return "🔴 Rojo", "Mal estado de forma"
    elif desfase >= 4:
        return "🟠 Naranja", "Estado de forma a mejorar"
    elif desfase >= -3:
        return "🟢 Verde", "Estado de forma correcto"
    elif desfase >= -9:
        return "🔘 Plateado", "Estado de forma bueno"
    else:
        return "🟡 Dorado", "Estado de forma excelente"

def calcular_edad_fisica(edad_real, flex, dom, sent, min_carrera, seg_carrera):
    tiempo_seg = (min_carrera * 60) + seg_carrera
    
    e_flex = interpolar_edad_prueba(flex, "flexiones")
    e_dom = interpolar_edad_prueba(dom, "dominadas")
    e_sent = interpolar_edad_prueba(sent, "sentadillas")
    e_carr = interpolar_edad_prueba(tiempo_seg, "carrera_seg", es_inverso=True)
    
    edad_fisica_total = (e_flex + e_dom + e_sent + e_carr) / 4.0
    desfase = edad_fisica_total - edad_real
    color, estado = obtener_zona_color(desfase)
    
    return round(edad_fisica_total, 1), round(desfase, 1), color, estado, (e_flex, e_dom, e_sent, e_carr)

# --- INTERFAZ DE USUARIO ---
st.title("🏃 Calculadora de Edad Física")
st.markdown("Descubre cuál es tu verdadera edad física en base a tu rendimiento deportivo.")

st.subheader("1. Datos Personales")
edad_real = st.number_input("Tu edad real (cronológica):", min_value=15, max_value=90, value=30)

st.subheader("2. Resultados de las Pruebas")
col1, col2 = st.columns(2)

with col1:
    flexiones = st.number_input("Flexiones (máx. rep):", min_value=0, value=20)
    sentadillas = st.number_input("Sentadillas en 1 min:", min_value=0, value=30)

with col2:
    dominadas = st.number_input("Dominadas (máx. rep):", min_value=0, value=5)
    st.markdown("**Carrera 5 km**")
    c_min, c_seg = st.columns(2)
    min_carrera = c_min.number_input("Minutos:", min_value=10, value=28)
    seg_carrera = c_seg.number_input("Segundos:", min_value=0, max_value=59, value=0)

if st.button("Calcular Edad Física", type="primary"):
    edad_fisica, desfase, color, estado, desglose = calcular_edad_fisica(
        edad_real, flexiones, dominadas, sentadillas, min_carrera, seg_carrera
    )
    
    st.divider()
    
    # Mostrar resultados principales
    st.header("Tus Resultados")
    
    # Métrica principal
    st.metric(label="Tu Edad Física Estimada", value=f"{edad_fisica} años", delta=f"{desfase} años respecto a tu edad", delta_color="inverse")
    
    st.subheader(f"Zona: {color} - {estado}")
    
    # Explicación extra
    if desfase < 0:
        st.success(f"¡Genial! Tu cuerpo rinde como el de alguien {abs(desfase)} años más joven.")
    elif desfase > 0:
        st.warning(f"Tu cuerpo rinde como el de alguien {desfase} años mayor. ¡Toca entrenar!")
    else:
        st.info("Tu edad física coincide exactamente con tu edad biológica.")

    # Desglose por pruebas
    st.markdown("### Desglose por prueba (Edad equivalente)")
    e_flex, e_dom, e_sent, e_carr = desglose
    
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("Flexiones", f"{round(e_flex, 1)} años")
    col_b.metric("Dominadas", f"{round(e_dom, 1)} años")
    col_c.metric("Sentadillas", f"{round(e_sent, 1)} años")
    col_d.metric("Carrera 5k", f"{round(e_carr, 1)} años")
