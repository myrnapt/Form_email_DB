from flask import Flask, request, render_template
# Importamos el conector de MySQL para conectar desde Python
import mysql.connector
# Importamos errores de MySQL para capturar fallos 
from mysql.connector import Error, errorcode

# Creamos la aplicación Flask (esto es obligatorio)
app = Flask(__name__)

# Función reutilizable: crea y devuelve una conexión nueva a MySQL
# Se usa en cada request para evitar dejar conexiones abiertas globalmente
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",      # MySQL corre dentro de WSL en localhost
        user="myrna",          # Usuario creado en MySQL
        password="proven",     # Password del usuario
        database="alumnes"     # Base de datos
    )

# Ruta 1: GETMAIL
# - GET: muestra el formulario para pedir nombre
# - POST: recibe el nombre, consulta la BD y muestra el email o error
@app.route("/getmail", methods=["GET", "POST"])
def getmail():
    # Variables que pasaremos a la plantilla; por defecto no hay resultado
    email = None
    error_msg = None
    nombre = ""

    # Si el usuario ha enviado el formulario, llega un POST
    if request.method == "POST":
        # Leemos el campo del formulario HTML: <input name="nombre">
        nombre = request.form["nombre"].strip()

        try:
            # Abrimos conexión a MySQL
            conn = get_db_connection()
            # Creamos cursor para ejecutar SQL
            cursor = conn.cursor()

            # Ejecutamos consulta parametrizada (evita inyección SQL)
            cursor.execute("SELECT email FROM contactes WHERE nom = %s", (nombre,))
            result = cursor.fetchone()  # Devuelve una fila (tuple) o None

            # Si no hay resultados, mostramos error
            if result is None:
                error_msg = "No existeix aquest nom a la BD"
            else:
                # result[0] contiene el email (única columna seleccionada)
                email = result[0]

        except Error as err:
            # Errores típicos si MySQL está apagado o credenciales incorrectas
            if err.errno == errorcode.CR_CONNECTION_ERROR:
                error_msg = "No es pot connectar: MySQL està apagat o no accessible"
            else:
                error_msg = f"Error MySQL: {err}"

        finally:
            # Cerramos recursos si llegaron a abrirse
            try:
                if cursor:
                    cursor.close()
            except:
                pass
            try:
                if conn and conn.is_connected():
                    conn.close()
            except:
                pass

    # Renderizamos la plantilla (muestra formulario y, si corresponde, resultado/error)
    return render_template("getmail.html", nombre=nombre, email=email, error_msg=error_msg)


# Ruta 2: ADDMAIL
# - GET: muestra formulario para añadir nombre+email
# - POST: inserta en BD; confirma o error si ya existe
@app.route("/addmail", methods=["GET", "POST"])
def addmail():
    ok_msg = None
    error_msg = None
    nombre = ""
    email = ""

    if request.method == "POST":
        # Leemos campos del formulario: <input name="nombre"> y <input name="email">
        nombre = request.form["nombre"].strip()
        email = request.form["email"].strip()

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Insert parametrizado
            cursor.execute(
                "INSERT INTO contactes (nom, email) VALUES (%s, %s)",
                (nombre, email)
            )
            # Confirmamos cambios (sin commit no se guarda)
            conn.commit()

            ok_msg = "Contacte afegit correctament"

            # Limpieza de campos tras insertar (para que el formulario vuelva vacío)
            nombre = ""
            email = ""

        except mysql.connector.errors.IntegrityError:
            # Esto pasa si 'nom' es UNIQUE y ya existe ese nombre
            error_msg = "Aquest nom ja existeix. Tria un altre."

        except Error as err:
            if err.errno == errorcode.CR_CONNECTION_ERROR:
                error_msg = "No es pot connectar: MySQL està apagat o no accessible"
            else:
                error_msg = f"Error MySQL: {err}"

        finally:
            try:
                if cursor:
                    cursor.close()
            except:
                pass
            try:
                if conn and conn.is_connected():
                    conn.close()
            except:
                pass

    return render_template("addmail.html", nombre=nombre, email=email, ok_msg=ok_msg, error_msg=error_msg)


# Arranque local en debug (en desarrollo)
if __name__ == "__main__":
    app.run(debug=True)
