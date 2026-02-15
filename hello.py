from flask import Flask, request, render_template
import mysql.connector

app = Flask(__name__)

#Función para conectarDB a la BD
def conectarDB():
    return mysql.connector.connect(
        host="localhost",
        user="myrna",
        password="proven",
        database="alumnes"
    )

@app.route("/getmail", methods=["GET", "POST"])
def getmail():
    email = None #que se muestre el formulario inicialmente vacío
    error = None #mensaje si hay un error

    if request.method == "POST":
        nombre = request.form["nombre"] #obtener el nombre del formulario
        conn = conectarDB() #guarda el resultado que produce la función en la var
        cursor = conn.cursor() #guardamos el metodo cursor para ejecutar consultas SQL
        cursor.execute(f"SELECT email FROM contactes WHERE nom = '{nombre}'")
        resultado = cursor.fetchone() #devuelve la primera fila del resultado de la consulta o None si no hay resultados

        #mensaje de error si no existe el nombre
        if resultado:
            email = resultado[0]
        else:
            error = "Nom no trobat"

        cursor.close()
        conn.close()

    return render_template("getmail.html", email=email, error=error) #devueve el html con las variables resultantes

@app.route("/addmail", methods=["GET", "POST"])
def addmail():
    mensaje = None

    if request.method == "POST":
        nombre = request.form["nombre"]
        email = request.form["email"]

        conn = conectarDB()
        cursor = conn.cursor()

        # Agregar el nuevo contacto a la base de datos
        cursor.execute(f"INSERT INTO contactes (nom, email) VALUES ('{nombre}', '{email}')")
        conn.commit()

        mensaje = "Contacte afegit correctament"

        cursor.close()
        conn.close()

    return render_template("addmail.html", mensaje=mensaje)

if __name__ == "__main__":
    app.run(debug=True)