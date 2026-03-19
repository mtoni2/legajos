import os

# --- CONFIGURACIÓN ---
archivo_datos = "datos_profes.txt"
carpeta_raiz = "Legajos"
archivo_html_principal = "index.html"

# 1. EMAILS AUTORIZADOS
emails_autorizados = ["marcelotoni2@gmail.com"]

# 2. CONFIGURACIÓN FIREBASE (Tus datos reales extraídos del index.html)
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

# Leer datos de los profesores (CUIL y Teléfono)
diccionario_profes = {}
if os.path.exists(archivo_datos):
    with open(archivo_datos, "r", encoding="utf-8") as f:
        for linea in f:
            partes = linea.strip().split(",")
            if len(partes) == 3:
                nombre, cuil, tel = partes[0].strip(), partes[1].strip(), partes[2].strip()
                diccionario_profes[nombre] = {"cuil": cuil, "tel": tel}

if not os.path.exists(carpeta_raiz):
    os.makedirs(carpeta_raiz)

try:
    profesores = sorted(list(diccionario_profes.keys()))

    # ENCABEZADO: Exactamente como el archivo que me pasaste
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
            background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), 
                        url('https://images.unsplash.com/photo-1568667256549-094345857637?q=80&w=2030') no-repeat center center fixed;
            background-size: cover; color: white; text-align: center; padding: 20px;
        }}
        .login-card {{ 
            border: none; border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.5); 
            max-width: 450px; width: 100%; color: #333; background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(5px);
        }}
        .btn-google {{ 
            background: white; color: #444; border: 1px solid #ddd; padding: 12px 25px; 
            font-weight: bold; border-radius: 8px; transition: 0.3s; 
            display: inline-flex; align-items: center; justify-content: center;
        }}
        .btn-google:hover {{ background: #f8f9fa; box-shadow: 0 4px 8px rgba(0,0,0,0.1); transform: translateY(-1px); }}
        #dashboard {{ display: none; }}
        .main-header {{ background: #1a252f; color: white; padding: 1.5rem; border-bottom: 5px solid #007bff; }}
        .card-profesor {{ border: none; border-left: 5px solid #007bff; transition: 0.3s; cursor: pointer; text-decoration: none; color: inherit; }}
        .card-profesor:hover {{ transform: translateY(-5px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <div id="login-page">
        <h1 class="mb-2 fw-bold" style="text-shadow: 2px 2px 10px rgba(0,0,0,0.8);">Sistema de Legajos Digitales</h1>
        <h3 class="mb-5" style="text-shadow: 2px 2px 8px rgba(0,0,0,0.8);">C.E.N.S. 3-484 "Laila Abusamra"</h3>
        <div class="card login-card p-5">
            <div class="mb-4"><span style="font-size: 3rem;">🔐</span><h4 class="mt-2 fw-bold">Acceso Restringido</h4></div>
            <p class="text-muted mb-4">Inicie sesión para gestionar la documentación docente.</p>
            <button onclick="login()" class="btn btn-google shadow-sm">
                <img src="https://fonts.gstatic.com/s/i/productlogos/googleg/v6/24px.svg" width="22" class="me-3"> Entrar con Google
            </button>
            <p id="errorMsg" class="text-danger mt-3" style="display:none; font-weight: bold;">⚠️ Usuario no autorizado</p>
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
                <input type="text" id="searchInput" class="form-control border-start-0" placeholder="Buscar profesor por nombre..." onkeyup="filterCards()">
            </div>
            <div class="row g-3" id="profList">
    """

    html_items = ""
    for nombre in profesores:
        cuil = diccionario_profes[nombre]["cuil"]
        tel = diccionario_profes[nombre]["tel"]
        nombre_carpeta = nombre.replace(" ", "_")
        ruta_profe = os.path.join(carpeta_raiz, nombre_carpeta)
        if not os.path.exists(ruta_profe): os.makedirs(ruta_profe)

        # Generar Ficha.html con el diseño de la imagen que me pasaste
        ficha_path = os.path.join(ruta_profe, "Ficha.html")
        with open(ficha_path, "w", encoding="utf-8") as f_p:
            f_p.write(f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <title>Ficha - {nombre}</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                <style>
                    body {{ background: #f4f7f6; padding: 40px; font-family: 'Segoe UI', sans-serif; }}
                    .ficha-card {{ background: white; border-radius: 15px; padding: 40px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); max-width: 800px; margin: auto; }}
                    .header-profe {{ border-bottom: 3px solid #007bff; padding-bottom: 15px; margin-bottom: 25px; color: #1a252f; }}
                    .btn-volver {{ background: #1a252f; color: white; border: none; }}
                    .btn-volver:hover {{ background: #2c3e50; color: white; }}
                </style>
            </head>
            <body>
                <div class="ficha-card text-center shadow">
                    <div class="fs-1 mb-3">👤</div>
                    <h2 class="header-profe">Expediente del Docente</h2>
                    <h3 class="mb-4">{nombre}</h3>
                    <div class="text-start mx-auto" style="max-width: 400px;">
                        <p><strong>Institución:</strong> <span class="float-end">C.E.N.S. 3-484</span></p>
                        <p><strong>CUIL:</strong> <span class="float-end text-primary fw-bold">{cuil}</span></p>
                        <p><strong>Teléfono:</strong> <span class="float-end">{tel}</span></p>
                    </div>
                    <div class="alert alert-warning mt-4 py-2">
                        <span class="me-2">📂</span> Carpeta digital en proceso de digitalización.
                    </div>
                    <a href="../../index.html" class="btn btn-volver mt-3 px-4">⬅️ Regresar al Archivo</a>
                </div>
            </body>
            </html>
            """)

        # Item de la lista principal
        html_items += f"""
                <div class="col-md-4 prof-card">
                    <a href="./{carpeta_raiz}/{nombre_carpeta}/Ficha.html" class="card card-profesor p-3 shadow-sm h-100">
                        <div class="d-flex align-items-center">
                            <div class="fs-2 me-3">📁</div>
                            <div>
                                <h6 class="mb-0 fw-bold">{nombre}</h6>
                                <small class="text-muted">CUIL: {cuil}</small>
                            </div>
                        </div>
                    </a>
                </div>"""

    # SCRIPTS DE CIERRE: Exactamente como tu archivo original
    html_fin = f"""
            </div>
        </div>
    </div>
    <script>
        {firebase_config}
        firebase.initializeApp(firebaseConfig);
        const auth = firebase.auth();
        function login() {{
            const provider = new firebase.auth.GoogleAuthProvider();
            auth.signInWithPopup(provider);
        }}
        function logout() {{ auth.signOut(); }}
        function filterCards() {{
            let input = document.getElementById('searchInput').value.toLowerCase();
            let cards = document.getElementsByClassName('prof-card');
            for (let card of cards) {{
                let name = card.innerText.toLowerCase();
                card.style.display = name.includes(input) ? "" : "none";
            }}
        }}
        auth.onAuthStateChanged(user => {{
            const dashboard = document.getElementById('dashboard');
            const loginPage = document.getElementById('login-page');
            if (user) {{
                const permitidos = {emails_autorizados};
                if (permitidos.includes(user.email)) {{
                    loginPage.style.display = 'none';
                    dashboard.style.display = 'block';
                }} else {{
                    document.getElementById('errorMsg').style.display = 'block';
                    auth.signOut();
                }}
            }} else {{
                loginPage.style.display = 'flex';
                dashboard.style.display = 'none';
            }}
        }});
    </script>
</body>
</html>"""

    with open(archivo_html_principal, "w", encoding="utf-8") as f:
        f.write(html_inicio + html_items + html_fin)

    print(f"✅ ¡Sistema restaurado y actualizado! Profesores: {len(profesores)}")

except Exception as e:
    print(f"❌ Error: {e}")