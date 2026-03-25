import os

# --- CONFIGURACIÓN DE ARCHIVOS ---
archivo_datos_admin = "datos_administradores.txt"
archivo_datos_personal = "datos_personal.txt"
carpeta_raiz = "Legajos"
archivo_html_principal = "index.html"

# 1. CONFIGURACIÓN FIREBASE
# Se mantienen tus credenciales originales del proyecto 'legajos-escuela'
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
    """
    Corrige errores de tipeo detectados en los archivos de origen
    como 'gmial' o la falta de punto en 'gmailcom'.
    """
    email = email.strip().lower()
    email = email.replace("gmial.com", "gmail.com")
    email = email.replace("gmailcom", "gmail.com")
    return email

# Estructuras para organizar la información de los TXT
diccionario_total = {}
lista_admins = []
mapeo_personal = []

def procesar_fuentes(nombre_archivo, es_admin):
    """
    Lee los archivos, extrae los datos y clasifica entre 
    Administradores (acceso total) y Personal (acceso único).
    """
    if not os.path.exists(nombre_archivo):
        print(f"⚠️ Archivo no encontrado: {nombre_archivo}")
        return
    
    with open(nombre_archivo, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("[source"): 
                continue
            
            try:
                # Formato: CUIL NOMBRE, TELEFONO, EMAIL
                partes = linea.split(",")
                primer_bloque = partes[0].split(" ", 1)
                
                if len(primer_bloque) == 2:
                    cuil = primer_bloque[0].strip()
                    nombre = primer_bloque[1].strip()
                    
                    # Extracción segura de Teléfono y Email
                    tel = partes[1].strip() if len(partes) > 1 and partes[1].strip() else "S/D"
                    email_crudo = partes[2].strip() if len(partes) > 2 and partes[2].strip() else ""
                    email = corregir_email(email_crudo) if email_crudo else "Sin Email"
                    
                    # Nombre de carpeta sin espacios para evitar errores en URL
                    folder_name = nombre.replace(" ", "_")
                    
                    if email_crudo:
                        if es_admin:
                            lista_admins.append(email)
                        else:
                            mapeo_personal.append({"e": email, "f": folder_name})
                    
                    diccionario_total[nombre] = {
                        "cuil": cuil, 
                        "tel": tel, 
                        "email": email,
                        "folder": folder_name
                    }
            except Exception as e:
                print(f"Error en línea: {linea} -> {e}")
                continue

# Procesar ambas bases de datos
procesar_fuentes(archivo_datos_admin, True)
procesar_fuentes(archivo_datos_personal, False)

# Crear directorio base
if not os.path.exists(carpeta_raiz):
    os.makedirs(carpeta_raiz)

try:
    nombres_ordenados = sorted(list(diccionario_total.keys()))

    # --- CONSTRUCCIÓN DEL INDEX.HTML ---
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
            background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                        url('https://images.unsplash.com/photo-1568667256549-094345857637') no-repeat center fixed;
            background-size: cover; color: white; text-align: center;
        }}
        .login-card {{ border: none; border-radius: 20px; max-width: 450px; width: 100%; color: #333; background: rgba(255, 255, 255, 0.95); }}
        
        #dashboard {{ 
            display: none; 
            padding-bottom: 150px; /* Margen inferior para scroll */
        }}
        
        .main-header {{ background: #1a252f; color: white; padding: 1.5rem; border-bottom: 5px solid #007bff; }}
        .card-profesor {{ border: none; border-left: 5px solid #007bff; transition: 0.3s; cursor: pointer; text-decoration: none; color: inherit; }}
        .card-profesor:hover {{ transform: translateY(-5px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        .dato-adicional {{ font-size: 0.85rem; color: #555; }}
        .badge-tel {{ background-color: #e7f1ff; color: #007bff; padding: 2px 8px; border-radius: 10px; font-weight: bold; }}
    </style>
</head>
<body>
    <div id="login-page">
        <h1 class="mb-5 fw-bold" style="text-shadow: 2px 2px 10px #000;">Sistema de Legajos Digitales</h1>
        <div class="card login-card p-5 shadow">
            <h4 class="mb-4 fw-bold">🔐 Acceso al Sistema</h4>
            <button onclick="login()" class="btn btn-dark btn-lg w-100 shadow">Entrar con Google</button>
            <p id="errorMsg" class="text-danger mt-3" style="display:none; font-weight: bold;">⚠️ Usuario no autorizado para este panel.</p>
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
            <div class="input-group mb-4 shadow-sm">
                <span class="input-group-text bg-white border-end-0">🔍</span>
                <input type="text" id="searchInput" class="form-control border-start-0" placeholder="Buscar por nombre, CUIL o teléfono..." onkeyup="filterCards()">
            </div>
            <div class="row g-3" id="profList">
    """

    html_items = ""
    for nombre in nombres_ordenados:
        info = diccionario_total[nombre]
        ruta_persona = os.path.join(carpeta_raiz, info["folder"])
        
        if not os.path.exists(ruta_persona):
            os.makedirs(ruta_persona)

        # Escaneo de archivos internos para la Ficha
        ext_permitidas = ('.pdf', '.jpg', '.jpeg', '.png')
        archivos = [f for f in os.listdir(ruta_persona) if f.lower().endswith(ext_permitidas) and f != "Ficha.html"]
        
        lista_doc_html = ""
        if archivos:
            for a in archivos:
                lista_doc_html += f"""
                <div class="py-2 border-bottom d-flex justify-content-between align-items-center">
                    <span>{a}</span>
                    <a href="./{a}" target="_blank" class="btn btn-sm btn-outline-primary">Abrir</a>
                </div>"""
        else:
            lista_doc_html = '<div class="alert alert-light text-center">No hay documentos cargados en esta carpeta.</div>'

        # Generación de Ficha.html
        with open(os.path.join(ruta_persona, "Ficha.html"), "w", encoding="utf-8") as f_f:
            f_f.write(f"""
            <html><head><meta charset='UTF-8'><link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css' rel='stylesheet'>
            <style>body{{background:#f8f9fa; padding:40px;}} .card-f{{max-width:700px; margin:auto; background:white; padding:40px; border-radius:20px; border:none; shadow:0 10px 30px rgba(0,0,0,0.05);}}</style>
            </head><body><div class='card-f shadow-lg'>
            <h2 class='fw-bold text-dark'>{nombre}</h2>
            <div class='row mt-3'>
                <div class='col-6'><p class='mb-1'><b>CUIL:</b> {info['cuil']}</p></div>
                <div class='col-6'><p class='mb-1'><b>Teléfono:</b> {info['tel']}</p></div>
                <div class='col-12'><p><b>Email:</b> {info['email']}</p></div>
            </div>
            <hr><h5>📄 Documentos Disponibles:</h5>
            {lista_doc_html}
            <div class='text-center mt-5'><button onclick='window.location.href="../../index.html"' class='btn btn-dark'>Regresar al Inicio</button></div>
            </div></body></html>""")

        # Item de la lista principal para el Admin
        html_items += f"""
                <div class="col-md-4 prof-card">
                    <a href="./{carpeta_raiz}/{info["folder"]}/Ficha.html" class="card card-profesor p-3 shadow-sm h-100">
                        <h6 class="mb-1 fw-bold text-truncate">{nombre}</h6>
                        <div class="dato-adicional">CUIL: {info['cuil']}</div>
                        <div class="mt-2"><span class="badge-tel">📞 {info['tel']}</span></div>
                    </a>
                </div>"""

    # Bloque final con Lógica de Seguridad Firebase
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
                    if (match) {{
                        window.location.href = `./{carpeta_raiz}/` + match.f + "/Ficha.html";
                    }} else {{
                        document.getElementById('errorMsg').style.display = 'block';
                        auth.signOut();
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>"""

    with open(archivo_html_principal, "w", encoding="utf-8") as f:
        f.write(html_inicio + html_items + html_fin)
    print(f"✅ Proceso terminado con éxito. {len(diccionario_total)} legajos procesados.")

except Exception as e:
    print(f"❌ Error durante la generación: {e}")