# 🗃️ Sistema de Legajos Digitales - C.E.N.S. 3-484 "Laila Abusamra"

Este proyecto es una plataforma web profesional diseñada para la gestión y consulta de legajos digitales del personal docente. Permite centralizar la documentación (DNI, Títulos, Certificados) de manera segura y organizada.

## 🚀 Acceso al Sistema
El sistema está desplegado y se puede acceder mediante el siguiente enlace:
🔗 **[https://mtoni2.github.io/legajos/](https://mtoni2.github.io/legajos/)**

> **Mensaje de Seguridad:** Al ingresar, verá el mensaje: *"Para acceder a los legajos, por favor identifíquese con su cuenta autorizada"*. Solo los correos electrónicos permitidos pueden visualizar el contenido.

---

## 🛠️ Funcionalidades Principales

* **Autenticación Segura:** Integración con Firebase Auth para permitir el ingreso mediante Google solo a personal autorizado.
* **Buscador Inteligente:** Filtro en tiempo real para localizar profesores por nombre de manera instantánea.
* **Fichas Individuales:** Cada docente cuenta con una ficha técnica que incluye Nombre, CUIL y Teléfono.
* **Escaneo de Documentos:** El sistema detecta automáticamente archivos PDF, JPG y PNG en las carpetas.
* **Nombres Limpios:** Se eliminan las extensiones (.pdf, .jpg) y se quitan los guiones bajos para que la lectura sea profesional.

---

## 📂 Estructura del Proyecto

* `generar_legajos.py`: Script de Python que procesa los datos y construye la web.
* `datos_profes.txt`: Archivo de texto con los datos de los docentes (Nombre, CUIL, Tel).
* `index.html`: Dashboard principal del archivero.
* `Legajos/`: Carpeta que contiene las subcarpetas de cada profesor con sus documentos.

---

## ⚙️ Instrucciones para Actualizar

1. **Agregar Documentos:** Colocar los archivos en la carpeta del profesor dentro de `/Legajos/`.
2. **Nombrar Archivos:** Usar nombres descriptivos (ej: `Titulo_Secundario.pdf`). El sistema los limpiará automáticamente.
3. **Ejecutar Python:** Correr `generar_legajos.py` para aplicar los cambios.
4. **Subir a la Web:** Abrir **GitHub Desktop**, realizar el *Commit* y luego el *Push*.

---

## 👨‍💻 Responsable del Proyecto
**Marcelo Tonini** - Desarrollador y Programador - Gestión de Legajos Digitales - C.E.N.S. 3-484
