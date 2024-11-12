import os
import re
from datetime import datetime, timedelta
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.secret_key = "sanamed"

# Configuración SQLAlchemy (Usar PostgreSQL con SQLAlchemy)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "postgresql://username:password@db:5432/sanamed")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

# Decorador para verificar rol de administrador
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or session.get('rol') != 'admin':
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Validación de contraseñas
def validate_password(password):
    if len(password) < 8:
        return False
    if not re.search("[A-Z]", password):
        return False
    if not re.search("[!@#$%^&*()_+=\[{\]};:<>|./?,-]", password):
        return False
    return True

@app.route('/admin_home')
@admin_required
def admin_home():
    if 'logged_in' in session and session['logged_in']:
        return render_template('admin_home.html')
    else:
        return redirect(url_for('index'))

@app.route('/profesionales')
@admin_required
def listar_profesionales():
    profesionales = db.session.execute(
        "SELECT id_profesional, nombre, especialidad FROM Profesionales"
    ).fetchall()
    return render_template('lista_profesionales.html', profesionales=profesionales)

@app.route('/agregar_profesional', methods=["GET", "POST"])
@admin_required
def agregar_profesional():
    if request.method == "POST":
        nombre = request.form['nombre']
        especialidad = request.form['especialidad']
        correo = request.form['correo']
        contrasena = request.form['contrasena']

        if not validate_password(contrasena):
            error = "La contraseña debe tener al menos 8 caracteres, incluyendo letras, números y caracteres especiales."
            return render_template('agregar_profesional.html', error=error)

        try:
            db.session.execute(
                "INSERT INTO Profesionales (nombre, especialidad, correo, contrasena) VALUES (:nombre, :especialidad, :correo, :contrasena)",
                {"nombre": nombre, "especialidad": especialidad, "correo": correo, "contrasena": contrasena}
            )
            db.session.commit()
            flash("Profesional agregado correctamente.", "success")
            return redirect(url_for('listar_profesionales'))
        except Exception as e:
            db.session.rollback()
            error = f"Error al agregar profesional: {str(e)}"
            return render_template('agregar_profesional.html', error=error)

    return render_template('agregar_profesional.html')

@app.route('/eliminar_profesional/<int:id>', methods=["POST"])
@admin_required
def eliminar_profesional(id):
    try:
        db.session.execute("DELETE FROM Profesionales WHERE id_profesional = :id", {"id": id})
        db.session.commit()
        flash("Profesional eliminado correctamente", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar profesional: {str(e)}", "error")
    return redirect(url_for('listar_profesionales'))

@app.route('/usuarios')
@admin_required
def listar_usuarios():
    usuarios = db.session.execute(
        "SELECT id_usuario, numero_documento, correo FROM Usuarios"
    ).fetchall()
    return render_template('lista_usuarios.html', usuarios=usuarios)

@app.route('/eliminar_usuario/<int:id>', methods=["POST"])
@admin_required
def eliminar_usuario(id):
    try:
        db.session.execute("DELETE FROM Usuarios WHERE id_usuario = :id", {"id": id})
        db.session.commit()
        flash('Usuario eliminado correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar usuario: {str(e)}", 'error')
    return redirect(url_for('listar_usuarios'))

@app.route('/citas_agendadas')
@admin_required
def listar_citas():
    query = """
    SELECT
        u.numero_documento,
        p.nombre AS nombre_profesional,
        c.fecha_consulta,
        c.hora_consulta,
        c.motivo,
        c.id_consulta
    FROM
        Consultas c
    JOIN
        Usuarios u ON c.id_usuario = u.id_usuario
    LEFT JOIN
        Profesionales p ON c.id_profesional = p.id_profesional
    """
    citas = db.session.execute(query).fetchall()
    return render_template('lista_consultas.html', citas=citas)

@app.route('/eliminar_cita/<int:id>', methods=['POST'])
@admin_required
def eliminar_cita(id):
    try:
        db.session.execute("DELETE FROM Consultas WHERE id_consulta = :id", {"id": id})
        db.session.commit()
        flash('La cita ha sido eliminada correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar cita: {str(e)}", 'error')
    return redirect(url_for('listar_citas'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
