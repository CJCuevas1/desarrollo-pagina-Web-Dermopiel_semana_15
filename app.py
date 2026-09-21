print("=== PROBANDO ARCHIVO CORRECTO ===")
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import mysql.connector
import forms
from conexion.conexion import get_db_connection
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = 'dermopiel-clave-secreta'

import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Configuración de conexión para PostgreSQL (local o Render)
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:12345@localhost:5432/dermopiel')

def get_db_connection():
    db_url = DATABASE_URL
    # Render usa 'postgres://' pero psycopg2 exige 'postgresql://'
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
    return conn
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


def get_db_connection():
    """Crea y retorna una conexión a la base de datos MySQL."""
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DATABASE']
    )

# --- CLASE DE USUARIO Y CARGADOR DE SESIÓN ---
class Usuario(UserMixin):
    def __init__(self, id, usuario, password):
        self.id = id
        self.usuario = usuario
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()
    if user_data:
        return Usuario(id=user_data['id'], usuario=user_data['usuario'], password=user_data['password'])
    return None

# --- RUTAS DE BASE DE DATOS Y MODULOS ---
@app.route('/test_db')
def test_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    cursor.close()
    conn.close()
    if not tables:
        return "¡Conexión exitosa a MySQL! La base de datos 'dermopiel' está conectada correctamente, pero aún no tiene tablas creadas."
    return f"¡Conexión exitosa! Tablas encontradas: {str(tables)}"

@app.route('/clientes')
def clientes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clientes")
    datos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('clientes.html', clientes=datos)

@app.route('/empleados')
def empleados():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM empleados")
    datos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('empleados.html', empleados=datos)

@app.route('/editar_empleado/<int:id_empleado>', methods=['GET', 'POST'])
def editar_empleado(id_empleado):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        nombres = request.form['nombres']
        apellidos = request.form['apellidos']
        cargo = request.form['cargo']
        telefono = request.form['telefono']
        email = request.form['email']

        cursor.execute("""
            UPDATE empleados
            SET nombres = %s, apellidos = %s, cargo = %s, telefono = %s, email = %s
            WHERE Id_empleado = %s
        """, (nombres, apellidos, cargo, telefono, email, id_empleado))
        conn.commit()
        cursor.close()
        conn.close()
        return "Empleado actualizado correctamente en MySQL"

    cursor.execute("SELECT * FROM empleados WHERE Id_empleado = %s", (id_empleado,))
    empleado = cursor.fetchone()
    cursor.close()
    conn.close()
    if empleado is None:
        return "Empleado no encontrado"
    return render_template('editar_empleado.html', empleado=empleado)

@app.route('/eliminar_empleado/<int:id_empleado>')
def eliminar_empleado(id_empleado):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM empleados WHERE Id_empleado = %s", (id_empleado,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/empleados')

@app.route('/servicios')
def servicios():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM servicios")
    datos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('servicios.html', servicios=datos)

@app.route('/editar_cliente/<int:id_cliente>', methods=['GET', 'POST'])
def editar_cliente(id_cliente):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        nombres = request.form['nombres']
        apellidos = request.form['apellidos']
        telefono = request.form['telefono']
        email = request.form['email']

        cursor.execute("""
            UPDATE clientes
            SET nombres = %s, apellidos = %s, telefono = %s, email = %s
            WHERE id_cliente = %s
        """, (nombres, apellidos, telefono, email, id_cliente))
        conn.commit()
        cursor.close()
        conn.close()
        return "Cliente actualizado correctamente en MySQL"

    cursor.execute("SELECT * FROM clientes WHERE id_cliente = %s", (id_cliente,))
    cliente = cursor.fetchone()
    cursor.close()
    conn.close()
    if cliente is None:
        return "Cliente no encontrado"
    return render_template('editar_cliente.html', cliente=cliente)

@app.route('/eliminar_cliente/<int:id_cliente>')
def eliminar_cliente(id_cliente):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientes WHERE id_cliente = %s", (id_cliente,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/clientes')

@app.route('/nuevo_cliente', methods=['GET', 'POST'])
def nuevo_cliente():
    form = ClienteForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO clientes (nombres, apellidos, telefono, email)
            VALUES (%s, %s, %s, %s)
        """, (form.nombres.data, form.apellidos.data, form.telefono.data, form.email.data))
        conn.commit()
        cursor.close()
        conn.close()
        return "Cliente guardado correctamente en MySQL"
    return render_template('clientes_form.html', titulo='Nuevo Cliente', form=form)

@app.route('/facturacion')
def facturacion():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT f.id_factura, c.nombres, c.apellidos, s.nombre_servicio, f.fecha, f.total
        FROM facturacion f
        INNER JOIN clientes c ON f.id_cliente = c.id_cliente
        INNER JOIN servicios s ON f.id_servicio = s.id_servicio
    """)
    datos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('facturacion.html', facturas=datos)

@app.route('/')
def inicio():
    return render_template('index.html')

# --- RUTAS DE AUTENTICACIÓN ---
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('inicio'))
    
    form = forms.RegistroForm()
    if form.validate_on_submit():
        usuario_input = form.usuario.data
        password_hashed = generate_password_hash(form.password.data)

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO usuarios (usuario, password) VALUES (%s, %s)", (usuario_input, password_hashed))
            conn.commit()
            return redirect(url_for('login'))
        except Exception:
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

    return render_template('registro.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    import importlib
    importlib.reload(forms)
    form = forms.LoginForm()

    form = forms.LoginForm()
    if form.validate_on_submit():
        usuario_input = form.usuario.data
        password_input = form.password.data

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s", (usuario_input,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()

        if user_data and check_password_hash(user_data['password'], password_input):
            usuario_obj = Usuario(id=user_data['id'], usuario=user_data['usuario'], password=user_data['password'])
            login_user(usuario_obj)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('inicio'))

    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- ARRANQUE DE LA APLICACIÓN AL FINAL ABSOLUTO ---
if __name__ == '__main__':
    print(app.url_map)
    app.run(debug=True)