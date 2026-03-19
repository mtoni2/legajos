import os

# --- CONFIGURACIÓN ---
archivo_lista = "profesores.txt"
carpeta_raiz = "Legajos"
archivo_html = "index.html"

# 1. PEGA AQUÍ LOS EMAILS AUTORIZADOS (Separados por coma)
emails_autorizados = ["marcelotoni2@gmail.com", "director@gmail.com"]

# 2. TUS DATOS DE FIREBASE (Los que ya tenías)
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

if not os.path.exists(carpeta_raiz):
    os.makedirs(carpeta_raiz)

try:
    with open(archivo_lista, "r", encoding="utf-8") as f:
        profesores = [line.strip() for line in f.readlines() if line.strip()]
    profesores.sort()

    html_inicio = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema de Legajos Docentes</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://www.gstatic.com/firebasejs/9.17.1/firebase-app-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.17.1/firebase-auth-compat.js"></script>
    <style>
        body {{ background-color: #f4f7f9; min-height: 100vh; font-family: 'Segoe UI', sans-serif; }}
        #login-page {{ display: flex; align-items: center; justify-content: center; height: 100vh; background: #2c3e50; }}
        #dashboard {{ display: none; }}
        .card-profesor {{ border: none; border-left: 5px solid #007bff; transition: 0.3s; cursor: pointer; }}
        .card-profesor:hover {{ transform: translateY(-3px); shadow: 0 4px 15px rgba(0,0,0,0.1); }}
        .navbar {{ background: #1a252f; }}
        .search-box {{ max-width: 500px; margin: 20px auto; }}
    </style>
</head>
<body>

    <div id="login-page">
        <div class="card shadow-lg p-5 text-center" style="border-radius: 15px;">
            <h2 class="mb-4 text-primary">🏫 Acceso Restringido</h2>
            <button onclick="login()" class="btn btn-outline-dark px-4 py-2">
                <img src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_广泛_logo.png" width="20" class="me-2">
                Entrar con Google
            </button>
            <p id="errorMsg" class="text-danger mt-3" style="display:none;">Acceso no autorizado</p>
        </div>
    </div>

    <div id="dashboard">
        <nav class="navbar navbar-dark shadow">
            <div class="container-fluid">
                <span class="navbar-brand">🗃️ Archivero Digital</span>
                <button onclick="logout()" class="btn btn-sm btn-outline-light">Cerrar Sesión</button>
            </div>
        </nav>

        <div class="container mt-4">
            <div class="search-box">
                <input type="text" id="searchInput" class="form-control" placeholder="🔍 Buscar profesor por nombre..." onkeyup="filterCards()">
            </div>
            <div class="row g-3" id="profList">
    """

    html_items = ""
    for nombre in profesores:
        nombre_carpeta = nombre.replace(" ", "_")
        ruta_legajo = os.path.join(carpeta_raiz, nombre_carpeta)
        if not os.path.exists(ruta_legajo):
            os.makedirs(ruta_legajo)
            os.makedirs(os.path.join(ruta_legajo, "Documentos"))
        
        html_items += f"""
                <div class="col-md-4 prof-card">
                    <a href="./{carpeta_raiz}/{nombre_carpeta}/Ficha.md" class="text-decoration-none text-dark">
                        <div class="card card-profesor p-3 shadow-sm">
                            <h6 class="mb-0">👤 {nombre}</h6>
                        </div>
                    </a>
                </div>"""

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
            const errorMsg = document.getElementById('errorMsg');
            
            if (user) {{
                const permitidos = {emails_autorizados};
                if (permitidos.includes(user.email)) {{
                    loginPage.style.display = 'none';
                    dashboard.style.display = 'block';
                }} else {{
                    errorMsg.style.display = 'block';
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

    with open(archivo_html, "w", encoding="utf-8") as f:
        f.write(html_inicio + html_items + html_fin)

    print(f"✅ ¡Todo listo! Se generaron {len(profesores)} legajos y la web protegida.")

except FileNotFoundError:
    print("❌ Error: Creá el archivo 'profesores.txt' con los nombres.")