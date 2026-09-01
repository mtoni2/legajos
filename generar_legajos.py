import os
import sys

# =================================================================
# --- 1. CONFIGURACIÓN DE RUTAS Y DATOS DE CONTACTO ---
# =================================================================
# Estos archivos deben existir en la misma carpeta que este script.
# Son la fuente de verdad para los permisos del sistema.
archivo_datos_admin = "datos_administradores.txt"
archivo_datos_personal = "datos_personal.txt"
carpeta_raiz = "Legajos"
archivo_html_principal = "index.html"

# ARCHIVO DEL LOGO (Marcelo: Asegurate que se llame logo.png en la carpeta)
ARCHIVO_LOGO = "logo.png"

# DATOS DE RECEPCIÓN (Configurados por Marcelo Tonini)
# El número debe incluir el código de país sin el signo + para WhatsApp
MI_WHATSAPP = "5492615458021" 
MI_EMAIL = "marcelotoni2@gmail.com"

# =================================================================
# --- 2. CONFIGURACIÓN FIREBASE (Hosting y Auth) ---
# =================================================================
# Mantenemos los IDs originales del proyecto legajos-escuela para
# que la autenticación con Google siga funcionando perfectamente.
firebase_config = """
  const firebaseConfig = {
    apiKey: "AIzaSyALCeluRao0L_ujIM7hQhCp9x9DahUclTg",
    authDomain: "legajos-escuela.firebaseapp.com",
    projectId: "legajos-escuela",
    storageBucket: "legajos-escuela.firebasestorage.app",
    messagingSenderId: "648427896776",
    appId: "1:648427896776:web:389a0c39500365935c4afd",
    measurementId: "G-ZS01PCVQWT"
  };
"""

# =================================================================
# --- 3. FUNCIONES DE UTILIDAD Y PROCESAMIENTO ---
# =================================================================

def corregir_email(email):
    """
    Limpia y normaliza los correos electrónicos para evitar errores 
    de acceso por espacios accidentales o errores de tipeo comunes.
    """
    if not email:
        return ""
    email = email.strip().lower()
    # Correcciones de dominios mal escritos detectados en el uso diario
    email = email.replace("gmial.com", "gmail.com")
    email = email.replace("gmailcom", "gmail.com")
    email = email.replace("gamil.com", "gmail.com")
    return email

def limpiar_nombre_archivo(nombre_raw):
    """
    Toma el nombre del archivo real (ej: dni_frente.pdf) y lo 
    transforma en algo elegante para mostrar al usuario (DNI FRENTE).
    """
    # 1. Quitamos la extensión (.pdf, .jpg, etc.)
    nombre_sin_ext = os.path.splitext(nombre_raw)[0]
    
    # 2. Reemplazamos guiones bajos y medios por espacios
    nombre_con_espacios = nombre_sin_ext.replace("_", " ").replace("-", " ")
    
    # 3. Lo pasamos a Mayúsculas para una mejor estética
    return nombre_con_espacios.upper()
def buscar_y_limpiar_nombre(carpeta, palabras_clave):
    if not os.path.exists(carpeta): 
        return None, None
    
    for f in os.listdir(carpeta):
        if any(pc.lower() in f.lower() for pc in palabras_clave):
            # 1. Guardamos el nombre real para el link (ej: bono_sueldo.pdf)
            nombre_real = f 
            
            # 2. Creamos el nombre estético (ej: BONO SUELDO)
            nombre_sin_ext = os.path.splitext(f)[0]
            nombre_lindo = nombre_sin_ext.replace("_", " ").replace("-", " ").upper()
            
            return nombre_real, nombre_lindo
            
    return None, None
# Estructuras de datos para organizar la información leída de los TXT
diccionario_total = {}
lista_admins = []
mapeo_personal = []

def procesar_fuentes_de_datos(nombre_archivo, es_admin):
    if not os.path.exists(nombre_archivo):
        print(f"⚠️ Aviso: No se encontró el archivo: {nombre_archivo}")
        return
    
    try:
        with open(nombre_archivo, "r", encoding="utf-8") as f:
            for num_linea, linea in enumerate(f, 1):
                linea = linea.strip()
                if not linea or linea.startswith("[source"):
                    continue
                
                try:
                    # Dividimos por coma
                    partes = [p.strip() for p in linea.split(",")]
                    
                    # El primer pedazo siempre es "CUIL Nombre Apellido"
                    primer_segmento = partes[0].split(" ", 1)
                    
                    if len(primer_segmento) >= 2:
                        cuil = primer_segmento[0].strip()
                        nombre = primer_segmento[1].strip()
                        
                        # USAMOS ESTA LÓGICA PARA QUE NO FALLE SI FALTA UN DATO
                        tel = partes[1] if len(partes) > 1 else "S/D"
                        email = corregir_email(partes[2]) if len(partes) > 2 else ""
                        # Si no hay 4ta parte, ponemos "No asignado"
                        urgencia = partes[3] if len(partes) > 3 else "No asignado"
                        
                        folder_name = nombre.replace(" ", "_").upper()
                        
                        if email:
                            if es_admin:
                                if email not in lista_admins:
                                    lista_admins.append(email)
                            else:
                                mapeo_personal.append({"e": email, "f": folder_name})
                        
                        # Guardamos todo en el diccionario
                        diccionario_total[nombre] = {
                            "cuil": cuil,
                            "tel": tel,
                            "tel_urgencia": urgencia, # <--- El nuevo campo
                            "folder": folder_name
                        }
                except Exception:
                    print(f"❌ Error procesando línea {num_linea} en {nombre_archivo}")
                    continue
    except Exception as e:
        print(f"❌ Error crítico leyendo {nombre_archivo}: {e}")

# =================================================================
# --- 4. MOTOR DE GENERACIÓN DEL SISTEMA ---
# =================================================================

print("---------------------------------------------------------")
print("🚀 SISTEMA DE LEGAJOS DIGITALES - C.E.N.S. Laila Abusamra")
print("---------------------------------------------------------")

# 1. Cargar bases de datos desde los TXT
procesar_fuentes_de_datos(archivo_datos_admin, True)
procesar_fuentes_de_datos(archivo_datos_personal, False)

# 2. Asegurar que la carpeta raíz de Legajos exista
if not os.path.exists(carpeta_raiz):
    os.makedirs(carpeta_raiz)

try:
    # Ordenar alfabéticamente para que el panel principal sea fácil de usar
    nombres_ordenados = sorted(list(diccionario_total.keys()))

    # --- INICIO DE CONSTRUCCIÓN DEL PANEL PRINCIPAL (index.html) ---
    html_inicio = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Archivero Digital - C.E.N.S. Laila Abusamra</title>
    <link rel="icon" type="image/x-icon" href="favicon.ico">
    <link rel="apple-touch-icon" href="favicon.ico">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://www.gstatic.com/firebasejs/9.17.1/firebase-app-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.17.1/firebase-auth-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.17.1/firebase-firestore-compat.js"></script>
    <style>
        body {{ background-color: #f4f7f6; min-height: 100vh; font-family: 'Segoe UI', Tahoma, sans-serif; }}
        
        /* ESTILO PORTADA CON LOGO Y FONDO MEJORADO */
        #login-page {{
            display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh;
            background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url('https://images.unsplash.com/photo-1568667256549-094345857637') no-repeat center fixed;
            background-size: cover; color: white;
        }}
        .login-card {{ 
            border: none; 
            border-radius: 25px; 
            max-width: 450px; 
            width: 90%; 
            color: #333; 
            background: rgba(255, 255, 255, 0.9); /* Un toque de transparencia */
            backdrop-filter: blur(10px); /* Efecto de desenfoque detrás del cuadro */
            box-shadow: 0 20px 40px rgba(0,0,0,0.4); 
            padding: 40px !important;
        }}
        .logo-escuela {{
            max-width: 150px;
            margin-bottom: 20px;
            filter: drop-shadow(0 5px 15px rgba(0,0,0,0.1));
        }}
        
        #dashboard {{ display: none; padding-bottom: 50px; }}
        .main-header {{ background: #1a252f; color: white; padding: 1.5rem; border-bottom: 5px solid #007bff; }}
        .card-profesor {{ border: none; border-left: 5px solid #007bff; transition: all 0.3s ease; cursor: pointer; text-decoration: none; color: inherit; background: white; }}
        .card-profesor:hover {{ transform: translateY(-5px); box-shadow: 0 8px 20px rgba(0,0,0,0.15); border-left-color: #25D366; }}
    </style>
</head>
<body>
    <div id="login-page">
        <div class="card login-card text-center">
            <img src="{ARCHIVO_LOGO}" alt="Logo CENS" class="logo-escuela mx-auto d-block">
            <h4 class="mb-2 fw-bold">BIENVENIDO</h4>
            <p class="text-muted small mb-4">Sistema de Legajos Digitales <br> <b>C.E.N.S. 3-484 "Laila Abusamra"</b></p>
            <button onclick="login()" class="btn btn-primary btn-lg w-100 shadow-sm rounded-pill py-3">Entrar con Google</button>
            <p id="errorMsg" class="text-danger mt-3" style="display:none; font-weight: bold;">⚠️ Error: Usuario no autorizado.</p>
        </div>
        <p class="mt-4 small opacity-75">Provincia de Mendoza, Argentina</p> 
        <p class="mt-4 small opacity-75"><b>© 2026 - Desarrollado por Marcelo Tonini</b></p>
    </div>

    <div id="dashboard">
        <div class="main-header shadow">
            <div class="container d-flex justify-content-between align-items-center">
                <div>
                    <h2 class="mb-0 fw-bold">🗃️ Panel de Gestión</h2>
                    <p class="mb-0 opacity-75 small text-uppercase">Área Administrativa</p>
                </div>
                <button onclick="logout()" class="btn btn-outline-light px-4 rounded-pill">Cerrar Sesión</button>
            </div>
        </div>

        <div class="container mt-4">
            <input type="text" id="searchInput" class="form-control form-control-lg shadow-sm rounded-pill mb-4" placeholder="🔍 Buscar por nombre o CUIL..." onkeyup="filterCards()">
            <div class="row g-4" id="profList">
    """

    html_items = ""
    for nombre in nombres_ordenados:
        info = diccionario_total[nombre]
        ruta_carpeta = os.path.join(carpeta_raiz, info["folder"])
        if not os.path.exists(ruta_carpeta):
            os.makedirs(ruta_carpeta)

        # --- NUEVA LÓGICA DE LISTA DE CONTROL (REEMPLAZO) ---
        documentos_requeridos = [
            ("Bono de Puntaje", ["bono", "puntaje"]),
            ("Certificado de Aptitud Psicofísica", ["psico", "apto", "aptitud"]),
            ("Certificado de Antecedentes Penales", ["antecedentes", "penales"]),
            ("Declaración Jurada de Cargo", ["declaracion", "jurada", "ddjj"]),
            ("DNI", ["DNI","dni","documento"]),
            ("Ley Micaela", ["micaela"]),
            ("Ley Lucio", ["lucio"]),
            ("Prevención de Bullying", ["bullying", "acoso"])
        ]

        html_docs_render = '<div class="list-group shadow-sm">'
        for doc_nombre, keywords in documentos_requeridos:
            # Usamos tu función para buscar el archivo real y el nombre limpio
            nombre_real, nombre_estetico = buscar_y_limpiar_nombre(ruta_carpeta, keywords)
            
            # Agregamos el calendario solo si es el Psicofísico
            input_fecha = f'<input type="date" id="fecha_psico_{info["folder"]}" oninput="guardarEnNube(\'fecha_psico_{info["folder"]}\', this.value)" class="form-control form-control-sm mt-1" style="max-width:150px; border: 2px solid #0d6efd;">' if "Psicofísica" in doc_nombre else ""
            
            if nombre_real:
                # Si existe, botón verde con el nombre limpio que genera tu función
                btn = f'<a href="./{nombre_real}" target="_blank" class="btn btn-sm btn-success px-3 rounded-pill">✅ VER {nombre_estetico}</a>'
                borde = "border-success"
            else:
                # Si no existe, cruz roja de faltante
                btn = '<span class="badge bg-danger p-2 shadow-sm w-100">❌ FALTANTE</span>'
                borde = "border-danger"
            
            html_docs_render += f"""
            <div class="list-group-item d-flex justify-content-between align-items-center mb-2 border-start border-4 {borde} shadow-sm bg-white">
                <div class="small fw-bold">{doc_nombre} {input_fecha}</div>
                <div style="min-width: 120px; text-align: right;">{btn}</div>
            </div>"""
        html_docs_render += '</div>'
        # --- FIN DE LA NUEVA LÓGICA ---
        # --- GENERACIÓN DE CADA FICHA INDIVIDUAL (Ficha.html) ---
        ficha_path = os.path.join(ruta_carpeta, "Ficha.html")
        with open(ficha_path, "w", encoding="utf-8") as f_out:
            f_out.write(f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ficha - {nombre}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://www.gstatic.com/firebasejs/9.17.1/firebase-app-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.17.1/firebase-auth-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.17.1/firebase-firestore-compat.js"></script>
    <style>
        body {{ background: #eef2f7; padding: 20px; font-family: 'Segoe UI', sans-serif; }}
        .ficha-card {{ max-width: 500px; margin: 30px auto; background: white; padding: 35px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
        .header-docente {{ border-left: 5px solid #0d6efd; padding-left: 15px; margin-bottom: 25px; }}
        .btn-accion {{ border-radius: 12px; padding: 12px; display: block; text-decoration: none; text-align: center; margin-bottom: 10px; color: white; font-weight: bold; transition: 0.3s; }}
        .wa {{ background: #25D366; }} .mail {{ background: #ea4335; }}
        .footer-nav {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }}
        #btnVolverPanel {{ display: none; width: 100%; margin-bottom: 12px; border-radius: 50px; font-weight: bold; }}
        .btn-logout {{ width: 100%; border-radius: 50px; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="ficha-card shadow-lg">
        <h4 class="text-center fw-bold mb-4">Detalle del Legajo</h4>
        <div class="header-docente">
            <h5 class="fw-bold mb-1 text-primary text-uppercase">{nombre}</h5>
            <p class="mb-0 text-muted small"><strong>CUIL:</strong> {info['cuil']}</p>
            <p class="mb-0 text-success small"><strong>TELÉFONO:</strong> {info['tel']}</p>
            <p class="mb-0 text-danger small"><strong>URGENCIAS:</strong> {info['tel_urgencia']}</p>
        </div>

        <h6 class="fw-bold small text-muted text-uppercase mb-2">Documentos Digitales:</h6>
        {html_docs_render}

        <div class="mt-4">
            <h6 class="fw-bold small text-muted text-uppercase mb-2">Actualizar Documentación:</h6>
            <a href="https://wa.me/{MI_WHATSAPP}" target="_blank" class="btn-accion wa">🟢 Enviar por WhatsApp</a>
            <a href="mailto:{MI_EMAIL}" class="btn-accion mail">✉️ Enviar por Email</a>
        </div>

        <div class="footer-nav">
            <button id="btnVolverPanel" onclick="window.location.href='../../index.html'" class="btn btn-outline-primary py-2">← VOLVER AL PANEL CENTRAL</button>
            <button onclick="logoutFicha()" class="btn btn-danger btn-logout py-2">❌ CERRAR SESIÓN</button>
        </div>
    </div>
    <script>
        {firebase_config}
        firebase.initializeApp(firebaseConfig);
        
        const auth = firebase.auth();
        const db = firebase.firestore();
        const admins = {lista_admins};

        // FUNCIÓN PARA GUARDAR O BORRAR LA FECHA
        function guardarEnNube(idDoc, valor) {{
            // QUITAMOS EL IF QUE FRENABA EL BORRADO
            
            console.log("Actualizando en nube:", idDoc, valor);
            db.collection("fechas_psico").doc(idDoc).set({{
                fecha: valor, // Si valor es "", Google guardará un vacío
                actualizado: new Date().toLocaleString()
            }}).then(() => {{
                // Si hay valor (fecha), borde VERDE. Si está vacío (borrado), borde GRIS original.
                const colorBorde = valor ? "#25D366" : "#ddd";
                document.getElementById(idDoc).style.borderColor = colorBorde;
                console.log("Base de datos actualizada correctamente");
            }}).catch((error) => {{
                console.error("Error al actualizar:", error);
            }});
        }}

        auth.onAuthStateChanged(user => {{
            if (user) {{
                if (admins.includes(user.email.toLowerCase())) {{
                    document.getElementById('btnVolverPanel').style.display = 'block';
                }}
                
                // LEER LA FECHA AL CARGAR (Con ID dinámico y DOBLE LLAVE para Python)
                const idParaLeer = "fecha_psico_{info['folder']}";
                db.collection("fechas_psico").doc(idParaLeer).get().then((doc) => {{
                    if (doc.exists) {{
                        const campo = document.getElementById(idParaLeer);
                        if (campo) {{
                            campo.value = doc.data().fecha;
                            campo.style.borderColor = "#25D366";
                        }}
                    }}
                }}).catch(err => console.error("Error al leer:", err));

            }} else {{
                window.location.href = "../../index.html";
            }}
        }});

        function logoutFicha() {{ 
            auth.signOut().then(() => window.location.href = "../../index.html"); 
        }}
    </script>
</body>
</html>""")

        # 1. Preparamos el badge de teléfono (Verde con link o Gris sin link)
        if info["tel"] != "S/D":
            link_wa = f"https://wa.me/549{info['tel']}"
            badge_tel = f'<a href="{link_wa}" target="_blank" onclick="event.stopPropagation();" class="text-decoration-none"><span class="badge bg-success rounded-pill px-3">📞 {info["tel"]}</span></a>'
        else:
            badge_tel = f'<span class="badge bg-secondary rounded-pill px-3">📞 S/D</span>'

        # 2. Tarjeta para el Panel Principal (index.html)
        html_items += f"""
                <div class="col-md-6 col-lg-4 prof-card">
                    <a href="./{carpeta_raiz}/{info["folder"]}/Ficha.html" class="text-decoration-none">
                        <div class="card card-profesor p-4 h-100 shadow-sm">
                            <h6 class="fw-bold text-primary mb-1 text-uppercase">{nombre}</h6>
                            <p class="small text-muted mb-3">CUIL: {info['cuil']}</p>
                            <div class="d-flex align-items-center mt-auto">
                                <div class="me-auto">
                                    {badge_tel}
                                </div>
                                <span class="text-primary fw-bold small">GESTIONAR →</span>
                            </div>
                        </div>
                    </a>
                </div>"""

    # --- SCRIPT FINAL Y LÓGICA DE FIREBASE PARA INDEX.HTML ---
    html_fin = f"""
            </div>
        </div>
    </div>
    <script>
        {firebase_config}
        firebase.initializeApp(firebaseConfig);
        const auth = firebase.auth();
        const admins = {lista_admins};
        const personal = {mapeo_personal};

        function login() {{ auth.signInWithPopup(new firebase.auth.GoogleAuthProvider()); }}
        function logout() {{ auth.signOut().then(() => location.reload()); }}

        function filterCards() {{
            const q = document.getElementById('searchInput').value.toLowerCase();
            document.querySelectorAll('.prof-card').forEach(c => {{
                c.style.display = c.innerText.toLowerCase().includes(q) ? 'block' : 'none';
            }});
        }}

        auth.onAuthStateChanged(user => {{
            if (user) {{
                const email = user.email.toLowerCase();
                document.getElementById('login-page').style.display = 'none';
                document.getElementById('dashboard').style.display = 'block';
                if (!admins.includes(email)) {{
                    const match = personal.find(p => p.e === email);
                    if (match) window.location.href = `./{carpeta_raiz}/` + match.f + "/Ficha.html";
                    else {{ auth.signOut(); }}
                }}
            }}
        }});
    </script>
</body>
</html>"""

    # Guardar el archivo index.html generado
    with open(archivo_html_principal, "w", encoding="utf-8") as f:
        f.write(html_inicio + html_items + html_fin)

    print(f"---------------------------------------------------------")
    print(f"✅ ÉXITO TOTAL: Se han procesado {len(diccionario_total)} registros.")
    print(f"🎨 Portada actualizada con logo: {ARCHIVO_LOGO}")
    print(f"---------------------------------------------------------")

except Exception as e:
    print(f"❌ Error crítico durante la ejecución: {e}")