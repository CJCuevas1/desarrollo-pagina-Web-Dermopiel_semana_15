print("=== PROBANDO ARCHIVO CORRECTO ===")
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import mysql.connector
import forms

from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')

app.config['SECRET_KEY'] = os.getenv(
    'SECRET_KEY',
    'clave-desarrollo'
)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )



login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


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
        return Usuario(id=user_data['id'], usuario=user_data['nombre'], password=user_data['password'])
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
@app.route('/nuevo_empleado', methods=['GET', 'POST'])
def nuevo_empleado():
    form = forms.EmpleadoForm()

    if form.validate_on_submit():
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO empleados
            (nombres, apellidos, cargo, telefono, email)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            form.nombres.data,
            form.apellidos.data,
            form.cargo.data,
            form.telefono.data,
            form.email.data
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('empleados'))

    return render_template(
        'empleados_form.html',
        titulo='Nuevo Empleado',
        form=form
    )

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
@app.route('/nuevo_servicio', methods=['GET', 'POST'])
@login_required
def nuevo_servicio():
    form = forms.ServicioForm()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, nombres, apellidos FROM clientes")
    clientes = cursor.fetchall()

    if form.validate_on_submit():
        cliente_id = request.form.get('cliente_id')

        cursor.execute("""
            INSERT INTO servicios
            (nombre_servicio, descripcion, precio, cliente_id, usuario_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            form.nombre_servicio.data,
            form.descripcion.data,
            form.precio.data,
            cliente_id,
            current_user.id
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('servicios'))

    cursor.close()
    conn.close()

    return render_template(
        'servicios_form.html',
        titulo='Nuevo Servicio',
        form=form,
        clientes=clientes
    )
@app.route('/editar_servicio/<int:id_servicio>', methods=['GET', 'POST'])
@login_required
def editar_servicio(id_servicio):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nombre_servicio = request.form['nombre_servicio']
        descripcion = request.form['descripcion']
        precio = request.form['precio']

        cursor.execute("""
            UPDATE servicios
            SET nombre_servicio = %s,
                descripcion = %s,
                precio = %s
            WHERE id = %s
        """, (
            nombre_servicio,
            descripcion,
            precio,
            id_servicio
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('servicios'))

    cursor.execute(
        "SELECT * FROM servicios WHERE id = %s",
        (id_servicio,)
    )

    servicio = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        'editar_servicio.html',
        servicio=servicio
    )


@app.route('/eliminar_servicio/<int:id_servicio>')
@login_required
def eliminar_servicio(id_servicio):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM servicios WHERE id = %s",
        (id_servicio,)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('servicios'))
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
            WHERE id = %s
        """, (nombres, apellidos, telefono, email, id_cliente))
        conn.commit()
        cursor.close()
        conn.close()
        return "Cliente actualizado correctamente en MySQL"

    cursor.execute("SELECT * FROM clientes WHERE id = %s", (id_cliente,))
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
    cursor.execute("DELETE FROM clientes WHERE id = %s", (id_cliente,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/clientes')

@app.route('/nuevo_cliente', methods=['GET', 'POST'])
def nuevo_cliente():
    form = forms.ClienteForm()
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
        SELECT
            f.id AS id_factura,
            c.nombres,
            c.apellidos,
            s.nombre_servicio,
            f.fecha,
            f.total
        FROM facturacion f
        INNER JOIN clientes c
            ON f.cliente_id = c.id
        INNER JOIN servicios s
            ON f.servicio_id = s.id
    """)

    datos = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'facturacion.html',
        facturas=datos
    )


@app.route('/nueva_factura', methods=['GET', 'POST'])
@login_required
def nueva_factura():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        servicio_id = request.form['servicio_id']
        fecha = request.form['fecha']
        total = request.form['total']

        cursor.execute("""
            INSERT INTO facturacion
            (cliente_id, servicio_id, fecha, total)
            VALUES (%s, %s, %s, %s)
        """, (
            cliente_id,
            servicio_id,
            fecha,
            total
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('facturacion'))

    cursor.execute("""
        SELECT id, nombres, apellidos
        FROM clientes
    """)
    clientes = cursor.fetchall()

    cursor.execute("""
        SELECT id, nombre_servicio
        FROM servicios
    """)
    servicios = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'facturacion_form.html',
        clientes=clientes,
        servicios=servicios
    )


@app.route('/editar_factura/<int:id_factura>', methods=['GET', 'POST'])
@login_required
def editar_factura(id_factura):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        servicio_id = request.form['servicio_id']
        fecha = request.form['fecha']
        total = request.form['total']

        cursor.execute("""
            UPDATE facturacion
            SET cliente_id = %s,
                servicio_id = %s,
                fecha = %s,
                total = %s
            WHERE id = %s
        """, (
            cliente_id,
            servicio_id,
            fecha,
            total,
            id_factura
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('facturacion'))

    cursor.execute(
        "SELECT * FROM facturacion WHERE id = %s",
        (id_factura,)
    )
    factura = cursor.fetchone()

    cursor.execute("""
        SELECT id, nombres, apellidos
        FROM clientes
    """)
    clientes = cursor.fetchall()

    cursor.execute("""
        SELECT id, nombre_servicio
        FROM servicios
    """)
    servicios = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'editar_factura.html',
        factura=factura,
        clientes=clientes,
        servicios=servicios
    )


@app.route('/eliminar_factura/<int:id_factura>')
@login_required
def eliminar_factura(id_factura):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM facturacion WHERE id = %s",
        (id_factura,)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('facturacion'))
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

        # Como el formulario no pide correo, generamos uno interno
        email_generado = f"{usuario_input}@dermopiel.local"

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO usuarios (nombre, email, password, rol)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    usuario_input,
                    email_generado,
                    password_hashed,
                    "usuario"
                )
            )

            conn.commit()
            return redirect(url_for('login'))

        except Exception as e:
            print("ERROR EN REGISTRO:", e)
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
        cursor.execute("SELECT * FROM usuarios WHERE nombre = %s", (usuario_input,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()

        if user_data and check_password_hash(user_data['password'], password_input):
            usuario_obj = Usuario(id=user_data['id'], usuario=user_data['nombre'], password=user_data['password'])
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