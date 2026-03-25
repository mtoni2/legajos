import os

# --- CONFIGURACIÓN DE ARCHIVOS ---
archivo_datos_admin = "datos_administradores.txt"
archivo_datos_personal = "datos_personal.txt"
carpeta_raiz = "Legajos"
archivo_html_principal = "index.html"

# 1. CONFIGURACIÓN FIREBASE (Mantener tus credenciales)
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

def corregir_email(email):
    """Limpia errores comunes en los correos electrónicos."""
    email = email.strip().lower()
    return email.replace("gmial.com", "gmail.com").replace("gmailcom", "gmail.com")

# Contenedores de datos
diccionario_total = {}
lista_admins = []
mapeo_personal = []

def procesar_fuentes(nombre_archivo, es_admin):
    """Lee los archivos TXT y prepara la estructura de carpetas y permisos."""
    if not os.path.exists(nombre_archivo):
        return
    
    with open(nombre_archivo, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("[source"): 
                continue
            
            try:
                # El formato es: CUIL NOMBRE, TELEFONO, EMAIL
                partes = linea.split(",")
                primer_segmento = partes[0].split(" ", 1)
                
                if len(primer_segmento) == 2:
                    cuil = primer_segmento[0].strip()
                    nombre = primer_segmento[1].strip()
                    tel = partes[1].strip() if len(partes) > 1 else "S/D"
                    email = corregir_email(partes[2]) if len(partes) > 2 else ""
                    
                    folder_name = nombre.replace(" ", "_")
                    
                    # Clasificación de permisos
                    if email:
                        if es_admin:
                            lista_admins.append(email)
                        else:
                            mapeo_personal.append({"e": email, "f": folder_name})
                    
                    # Guardar para generar carpetas e index
                    diccionario_total[nombre] = {
                        "cuil": cuil, 
                        "tel": tel, 
                        "folder": folder_name
                    }
            except Exception:
                continue

# Cargar ambos archivos de datos 
procesar_fuentes(archivo_datos_admin, True)
procesar_fuentes(archivo_datos_personal, False)

# Crear carpeta raíz si no existe
if not os.path.exists(carpeta_raiz):
    os.makedirs(carpeta_raiz)

try:
    nombres_ordenados = sorted(list(diccionario_total.keys()))

    # --- GENERACIÓN DE INDEX.HTML ---
    html_inicio = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema de Legajos - C.E.N.S. Laila Abusamra</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://www.gstatic.com/firebasejs/9.17.1/firebase-app-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.17.1/firebase-auth-compat.js"></script>
    <style>
        body {{ background-color: #f4f7f6; min-height: 100vh; font-family: 'Segoe UI', sans-serif; }}
        #login-page {{
            display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh;
            background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url('https://images.unsplash.com/photo-1568667256549-094345857637') no-repeat center fixed;
            background-size: cover; color: white; text-align: center;
        }}
        .login-card {{ border: none; border-radius: 20px; max-width: 450px; width: 100%; color: #333; background: rgba(255, 255, 255, 0.95); }}
        #dashboard {{ display: none; }}
        .main-header {{ background: #1a252f; color: white; padding: 1.5rem; border-bottom: 5px solid #007bff; }}
        .card-profesor {{ border: none; border-left: 5px solid #007bff; transition: 0.3s; cursor: pointer; text-decoration: none; color: inherit; }}
        .card-profesor:hover {{ transform: translateY(-5px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <div id="login-page">
        <h1 class="mb-5 fw-bold" style="text-shadow: 2px 2px 10px #000;">Sistema de Legajos Digitales</h1>
        <div class="card login-card p-5 shadow">
            <h4 class="mb-4 fw-bold">🔐 Acceso al Sistema</h4>
            <button onclick="login()" class="btn btn-dark btn-lg w-100">Entrar con Google</button>
            <p id="errorMsg" class="text-danger mt-3" style="display:none; font-weight: bold;">⚠️ Usuario no autorizado para este sistema.</p>
        </div>
    </div>
    <div id="dashboard">
        <div class="main-header shadow">
            <div class="container d-flex justify-content-between align-items-center">
                <h2 class="mb-0 fw-bold">🗃️ Archivero Digital</h2>
                <button onclick="logout()" class="btn btn-sm btn-outline-light">Cerrar Sesión</button>
            </div>
        </div>
        <div class="container mt-4">
            <input type="text" id="searchInput" class="form-control mb-4 shadow-sm" placeholder="Buscar por nombre..." onkeyup="filterCards()">
            <div class="row g-3" id="profList">
    """

    html_items = ""
    for nombre in nombres_ordenados:
        info = diccionario_total[nombre]
        ruta_carpeta = os.path.join(carpeta_raiz, info["folder"])
        
        # CREACIÓN FÍSICA DE LA CARPETA
        if not os.path.exists(ruta_carpeta):
            os.makedirs(ruta_carpeta)

        # Escaneo de archivos existentes (PDFs, imágenes)
        archivos_internos = ""
        ext_validas = ('.pdf', '.jpg', '.jpeg', '.png')
        lista_archivos = [f for f in os.listdir(ruta_carpeta) if f.lower().endswith(ext_validas) and f != "Ficha.html"]
        
        if lista_archivos:
            for arc in lista_archivos:
                limpio = os.path.splitext(arc)[0].replace("_", " ")
                archivos_internos += f"""
                <div class="py-2 border-bottom d-flex justify-content-between align-items-center">
                    <span style="text-transform: capitalize;">{limpio}</span>
                    <a href="./{arc}" target="_blank" class="btn btn-sm btn-outline-primary">Ver</a>
                </div>"""
        else:
            archivos_internos = '<div class="alert alert-light text-center small">Sin documentos cargados aún.</div>'

        # GENERACIÓN DE FICHA.HTML INDIVIDUAL
        ficha_path = os.path.join(ruta_carpeta, "Ficha.html")
        with open(ficha_path, "w", encoding="utf-8") as f_out:
            f_out.write(f"""
            <html><head><meta charset='UTF-8'><link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css' rel='stylesheet'>
            <style>body{{background:#f8f9fa; padding:30px;}} .c{{max-width:600px; margin:auto; background:white; padding:30px; border-radius:15px; shadow:0 2px 10px rgba(0,0,0,0.1);}}</style>
            </head><body><div class='c shadow'>
            <h3 class='text-center mb-4'>Expediente Digital</h3>
            <p><strong>Nombre:</strong> {nombre}</p>
            <p><strong>CUIL:</strong> {info['cuil']}</p>
            <p><strong>Teléfono:</strong> {info['tel']}</p>
            <hr><h5>Documentación:</h5>
            {archivos_internos}
            <div class='text-center mt-4'><button onclick='window.location.href="../../index.html"' class='btn btn-dark'>Volver al Inicio</button></div>
            </div></body></html>""")

        # Item para la cuadrícula del administrador
        html_items += f"""
                <div class="col-md-4 prof-card">
                    <a href="./{carpeta_raiz}/{info["folder"]}/Ficha.html" class="card card-profesor p-3 shadow-sm h-100">
                        <h6 class="mb-0 fw-bold">{nombre}</h6>
                        <small class="text-muted">CUIL: {info['cuil']}</small>
                    </a>
                </div>"""

    # SCRIPTS DE SEGURIDAD Y REDIRECCIÓN
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
        function logout() {{ auth.signOut(); location.reload(); }}
        function filterCards() {{
            let q = document.getElementById('searchInput').value.toLowerCase();
            document.querySelectorAll('.prof-card').forEach(c => {{
                c.style.display = c.innerText.toLowerCase().includes(q) ? "" : "none";
            }});
        }}

        auth.onAuthStateChanged(user => {{
            if (user) {{
                const email = user.email.toLowerCase();
                if (admins.includes(email)) {{
                    document.getElementById('login-page').style.display = 'none';
                    document.getElementById('dashboard').style.display = 'block';
                }} else {{
                    const match = personal.find(p => p.e === email);
                    if (match) window.location.href = `./{carpeta_raiz}/` + match.f + "/Ficha.html";
                    else document.getElementById('errorMsg').style.display = 'block';
                }}
            }}
        }});
    </script>
</body>
</html>"""

    with open(archivo_html_principal, "w", encoding="utf-8") as f:
        f.write(html_inicio + html_items + html_fin)
    print(f"✅ Proceso completado: {len(diccionario_total)} carpetas de legajos creadas/actualizadas.")

except Exception as e:
    print(f"❌ Error durante la ejecución: {e}")