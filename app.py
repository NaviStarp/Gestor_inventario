from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange
import csv
import os
from flask import flash
from functools import wraps
from flask import session
# Se crea la instancia de la aplicación Flask
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necesario para usar sesiones

# Base de datos 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventario.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Se crea la tabla Inventario
class Inventario(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(100), nullable=False)  # Número del inventario
    marca = db.Column(db.String(100), nullable=False)  # Marca del producto
    modelo = db.Column(db.String(100), nullable=False)  # Modelo del producto
    estado = db.Column(db.String(100), nullable=False)  # Estado del producto
    ubicacion = db.Column(db.String(100), nullable=False)  # Ubicación del producto
    observacion = db.Column(db.String(255), nullable=True)  # Observaciones opcionales
    numero_serie_f = db.Column(db.String(100), nullable=False)  # Número de serie del fabricante
    numero_serie_i = db.Column(db.String(100), nullable=False)  # Número de serie interno
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)  # Categoría del producto
    categoria = db.relationship('Categoria', backref=db.backref('inventarios', lazy=True)) # Relación con la tabla Categoría
    cliente = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=True)  # Cliente asociado
    precio = db.Column(db.Integer, nullable=False)  # Precio del producto

    def __repr__(self):
        return f'<Inventario {self.id}>'


class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255), nullable=True)
    productos = db.Column(db.Integer, nullable=False, default=0)
    
    def __repr__(self):
        return f'<Categoria {self.id}>'

class Movimiento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.relationship('Usuario', backref=db.backref('movimientos', lazy=True))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.now)
    acción = db.Column(db.String(100), nullable=False)
    departamento = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Movimiento {self.id}>'

# Se crea la tabla Cliente
class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    dni = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(100), nullable=False)
    id_cliente = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=True)  # Si es jerárquico
    nombre_cliente = db.relationship('Cliente', remote_side=[id], backref=db.backref('subclientes', lazy=True))
    prioridad = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Cliente {self.id}>'
class Contraseña(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contraseña = db.Column(db.String(100), nullable=False, default=generate_password_hash('Admin123'))
    @classmethod
    def create_default_password(cls):
        if not cls.query.first():
            default_password = cls(contraseña=generate_password_hash('Admin123'))
            db.session.add(default_password)
            print("Contraseña de administrador por defecto creada")
            db.session.commit()
        
# Se crea la tabla Alquiler
class Alquiler(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inventario_id = db.Column(db.Integer, db.ForeignKey('inventario.id'), nullable=False)
    inventario = db.relationship('Inventario', backref=db.backref('alquileres', lazy=True))
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    cliente = db.relationship('Cliente', backref=db.backref('alquileres', lazy=True))
    fecha_entrega = db.Column(db.Date, nullable=False)
    fecha_recojida = db.Column(db.Date, nullable=False)
    estado = db.Column(db.String(100), nullable=False)  # Corregido: Era "Estado" (inconsistente)
    precio = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Alquiler {self.id}>'
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    contraseña = db.Column(db.String(100), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    def repr(self):
        return super().repr()
    
# Formularios
class FilterForm(FlaskForm):
    estado = SelectField('Estado', choices=[
        ('', 'Todos'), 
        ('Pendiente', 'Pendiente'),
        ('Entregado', 'Entregado'),
        ('Devuelto', 'Devuelto'),
        ('Cancelado', 'Cancelado')
    ])
    fecha_desde = DateField('Desde', format='%Y-%m-%d', validators=[], render_kw={"type": "date"})
    fecha_hasta = DateField('Hasta', format='%Y-%m-%d', validators=[], render_kw={"type": "date"})
    submit = SubmitField('Filtrar')

class filtroInventario(FlaskForm):
    estado = SelectField('Estado', choices=[
        ('', 'Todos'), 
        ('Disponible', 'Disponible'),
        ('En uso', 'En uso'),
        ('Reparación', 'Reparación'),
        ('Baja', 'Baja')
    ])
    cliente = SelectField('Cliente', choices=[], coerce=int)
    categoria = SelectField('Categoria', choices=[], coerce=int)
    submit = SubmitField('Filtrar')
    
    def __init__(self, *args, **kwargs):
        super(filtroInventario, self).__init__(*args, **kwargs)
        # Reiniciar las opciones para evitar duplicados en recargas
        self.cliente.choices = [(0, 'Todos')]
        self.categoria.choices = [(0, 'Todas')]
        # Agregar opciones desde la base de datos
        self.cliente.choices += [(c.id, c.nombre) for c in Cliente.query.all()]
        self.categoria.choices += [(c.id, c.nombre) for c in Categoria.query.all()]

class filtroCliente(FlaskForm):
    prioridad = SelectField('Prioridad', choices=[
        ('', 'Todos'), 
        ('Alta', 'Alta'),
        ('Media', 'Media'),
        ('Baja', 'Baja')
    ])
    email = StringField('Email')
    nombre = StringField('Nombre')
    DNI = StringField('Dni')
    submit = SubmitField('Filtrar')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('inicio_sesion'))
        return f(*args, **kwargs)
    return decorated_function
# Ruta de inicio
@app.route('/')
@login_required
def inicio():
    categorias = Categoria.query.all()
    clientes = Cliente.query.all()
    inventarios = Inventario.query.all()
    alquileres = Alquiler.query.all()
    return render_template('index.html', alquileres=alquileres, categorias=categorias, clientes=clientes, inventarios=inventarios)
@app.route('/movimientos')
@login_required
def movimientos():
    movimientos = Movimiento.query.all()
    movimientos.sort(key=lambda x: x.fecha, reverse=True)
    return render_template('movimientos.html', movimientos=movimientos)

@app.route('/registro', methods=['GET','POST'])
def registro():
    if request.method == 'POST':
        usuario = Usuario.query.filter_by(nombre=request.form['nombre']).first()
        if usuario:
            return render_template('registro.html', error="El usuario ya existe")
        contraseña_record = Contraseña.query.first()
        if contraseña_record:
            # Use the correct order of arguments
            if check_password_hash(contraseña_record.contraseña, request.form['contraseña_admin']):
                nuevo_usuario = Usuario(
                    nombre=request.form['nombre'],
                    contraseña=generate_password_hash(request.form['contraseña']),
                    admin=True
                )
                db.session.add(nuevo_usuario)
                db.session.commit()
                return redirect(url_for('inicio_sesion'))
            else:
                return render_template('registro.html', error="Contraseña de administrador incorrecta")
        else:
            default_password = Contraseña(contraseña=generate_password_hash('Admin123')) # Cambiar contraseña para registrar
            db.session.add(default_password)
            db.session.commit()
            return render_template('registro.html', error="Se ha creado una contraseña de administrador por defecto. Inténtelo de nuevo.")
    else:
        return render_template('registro.html')

@app.route('/inicio-sesion', methods=['GET','POST'])
def inicio_sesion():
    if request.method == 'POST':
        try:
            usuario = Usuario.query.filter_by(nombre=request.form['nombre']).first()
            if usuario and usuario.contraseña and check_password_hash(usuario.contraseña, request.form['contraseña']):
                session['user_id'] = usuario.id
                session['admin'] = usuario.admin
                session['username'] = usuario.nombre
                return redirect('/')
            else:
                return render_template('iniciar sesion.html',error="Usuario o contraseña incorrectos")
        except Exception as e:
            error = str(e)
            return render_template('iniciar sesion.html', error=error)
    else:
        return render_template('iniciar sesion.html')
@app.route('/cerrar-sesion')
def cerrar_sesion():
    session.pop('user_id', None)
    session.pop('admin', None)
    session.pop('username', None)
    return redirect('/')


@app.route('/categoria/editar', methods=['POST'])
@login_required
def editar_categoria():
    categoria = Categoria.query.get_or_404(request.form['id'])
    categoria.nombre = request.form['nombre']
    categoria.descripcion = request.form.get('descripcion')
    movimiento = Movimiento(usuario_id=session['user_id'],acción=f"Editó la categoría {categoria.nombre}",departamento="Categorías")
    db.session.add(movimiento)
    db.session.commit()
    return redirect(request.referrer)

@app.route('/categoria/eliminar/<int:id>', methods=['GET','POST'])
@login_required
def eliminar_categoria(id):
    Inventario.query.filter_by(categoria_id=id).delete()
    categoria = Categoria.query.get_or_404(id)
    movimiento = Movimiento(usuario_id=session['user_id'],acción=f"Eliminó la categoría {categoria.nombre}",departamento="Categorías")
    db.session.add(movimiento)
    db.session.delete(categoria)
    db.session.commit()
    return redirect(request.referrer)

@app.route('/cliente/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    db.session.delete(cliente)
    movimiento = Movimiento(usuario_id=session['user_id'],acción=f"Eliminó el cliente {cliente.nombre}",departamento="Clientes")
    db.session.add(movimiento)
    db.session.commit()
    return redirect(request.referrer)
@app.route('/categorias/')
@login_required
def ver_categorias():
    categorias = Categoria.query.all()
    inventario = Inventario.query.all()
    for categoria in categorias:
        categoria.productos = Inventario.query.filter_by(categoria_id=categoria.id).count()
    return render_template('categorias.html', categorias=categorias)

@app.route('/inventario/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_producto(id):
    inventario = Inventario.query.get_or_404(id)
    categoria = Categoria.query.get(inventario.categoria_id)
    if inventario.categoria:
        categoria.productos -= 1
    alquileres = Alquiler.query.filter_by(inventario_id=id).all()
    for alquiler in alquileres:
        db.session.delete(alquiler)
    db.session.delete(inventario)
    movimiento = Movimiento(usuario_id=session['user_id'],acción=f"Eliminó el producto {inventario.numero}",departamento="Inventario")
    db.session.add(movimiento)
    db.session.commit()
    return redirect(request.referrer)

@app.route('/alquiler/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_alquiler(id):
    alquiler = Alquiler.query.get_or_404(id)
    db.session.delete(alquiler)
    movimiento = Movimiento(usuario_id=session['user_id'],acción=f"Eliminó el alquiler {alquiler.id}",departamento="Alquileres")
    db.session.add(movimiento)
    db.session.commit()
    return redirect(request.referrer)

# Ruta para ver inventario
@app.route('/inventario', methods=['GET', 'POST'])
@login_required
def ver_inventario():
    form = filtroInventario()
    
    # Iniciar con la consulta base
    query = Inventario.query
    
    # Procesar el formulario solo si se envía como POST
    if request.method == 'POST' and form.validate():
        if form.estado.data:
            query = query.filter(Inventario.estado == form.estado.data)
        if form.cliente.data and form.cliente.data != 0:  # Evitar filtrar cuando se selecciona "Todos"
            query = query.filter(Inventario.cliente_id == form.cliente.data)
        if form.categoria.data and form.categoria.data != 0:  # Evitar filtrar cuando se selecciona "Todas"
            query = query.filter(Inventario.categoria_id == form.categoria.data)
    
    # Ejecutar la consulta final
    inventarios = query.all()
    categorias = Categoria.query.all()
    clientes = Cliente.query.all()
    return render_template('inventario.html',clientes=clientes,categorias=categorias, inventarios=inventarios, form=form)

# Ruta para ver una categoría específica
@app.route('/categoria/<int:id>', methods=['GET', 'POST'])
@login_required
def ver_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    form = filtroInventario()
    
    # Iniciar con la consulta base filtrada por la categoría
    query = Inventario.query.filter_by(categoria_id=id)
    
    # Pre-seleccionar la categoría en el formulario
    form.categoria.data = id
    
    # Procesar el formulario si se envía como POST
    if request.method == 'POST' and form.validate():
        if form.estado.data:
            query = query.filter(Inventario.estado == form.estado.data)
        if form.cliente.data and form.cliente.data != 0:
            query = query.filter(Inventario.cliente_id == form.cliente.data)
        # No necesitamos filtrar por categoría de nuevo ya que ya está filtrado
    
    # Ejecutar la consulta final
    inventarios = query.all()
    
    return render_template('inventario.html', categoria=categoria, inventarios=inventarios, form=form,es_categoria=True)

# Ruta para ver clientes
@app.route('/clientes', methods=['GET', 'POST'])
@login_required
def ver_clientes():
    clientes = Cliente.query.all()
    form = filtroCliente()
    query = Cliente.query
    if request.method == 'POST' and form.validate():
        if form.prioridad.data:
            query = query.filter(Cliente.prioridad == form.prioridad.data)
        if form.email.data:
            query = query.filter(Cliente.email.like(f'%{form.email.data}%'))
        if form.nombre.data:
            query = query.filter(Cliente.nombre.like(f'%{form.nombre.data}%'))
        if form.DNI.data:
            query = query.filter(Cliente.dni == form.DNI.data)
    clientes = query.all()
    return render_template('clientes.html', clientes=clientes,form=form)

@app.route('/inventario/importar/csv', methods=['POST'])
@login_required
def importar_inventario():
    try:
        # Verificar si el archivo está en la solicitud
        if 'file' not in request.files:
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(request.referrer)
            
        archivo = request.files['file']
        
        # Verificar si el archivo tiene nombre y extensión válida
        if archivo.filename == '':
            flash('Nombre de archivo vacío', 'error')
            return redirect(request.referrer)
            
        if not archivo.filename.endswith('.csv'):
            flash('El archivo debe tener extensión .csv', 'error')
            return redirect(request.referrer)
            
        # Guardar archivo temporalmente
        if not os.path.exists('temp'):
            os.makedirs('temp')
            
        archivoBytes = f"temp/{archivo.filename}"
        archivo.save(archivoBytes)
        
        filas_procesadas = 0
        
        try:
            with open(archivoBytes, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Omitir la primera fila (encabezados)                
                for i, row in enumerate(reader, start=1):
                    # Evitar procesar filas vacías
                    if not any(row):
                        continue
                
                    try:
                        nuevo_producto = Inventario(
                            categoria_id=row[0] if row[0] else 1,
                            numero=row[1] if row[1] else None,
                            marca=row[2] if row[2] else None,
                            modelo=row[3] if row[3] else None,
                            estado=row[4] if row[4] else None,
                            precio=row[5] if row[5] else None,
                            ubicacion=row[6] if row[6] else None,
                            numero_serie_f=row[7] if row[7] else None,
                            numero_serie_i=row[8] if row[8] else None,
                            observacion=row[9] if row[9] else None,
                            cliente=None
                        )
                        if nuevo_producto.categoria_id is not None:
                            categoria = Categoria.query.get(nuevo_producto.categoria_id)
                            if categoria:
                                categoria.productos += 1
                        db.session.add(nuevo_producto)
                        filas_procesadas += 1
                    except Exception as e:
                        # Manejar errores específicos de fila
                        print(f"Error en la fila {i}: {e}")
                        continue
                
                # Commit una sola vez después de procesar todas las filas
                if filas_procesadas > 0:
                    movimiento = Movimiento(usuario_id=session['user_id'],acción=f"Importó {filas_procesadas} productos",departamento="Inventario")
                    db.session.add(movimiento)
                    db.session.commit()
                    flash(f'Se importaron {filas_procesadas} productos correctamente', 'success')
                else:
                    flash('No se importaron productos. Verifique el formato del archivo.', 'warning')
        finally:
            # Limpiar el archivo temporal
            if os.path.exists(archivoBytes):
                os.remove(archivoBytes)
                
        return redirect('/inventario')
        
    except Exception as e:
        db.session.rollback()  # Revertir cambios en caso de error
        print(f"Error al importar el archivo: {e}")
        flash(f'Error al importar: {str(e)}', 'error')
        return redirect(request.referrer)
    
    
@app.route('/inventario/importar', methods=['GET'])
@login_required
def importar_vista():
    return render_template('importar.html')

# Ruta para añadir producto al inventario
@app.route('/inventario/nuevo', methods=['POST'])
@login_required
def crear_producto():
    try:
        print("Datos recibidos:", request.form)
        cliente = Cliente.query.filter_by(id=request.form.get('cliente_id')).first()
        nuevo_producto = Inventario(
            categoria_id=request.form['categoria_id'],
            numero=request.form.get('numero', ''),
            marca=request.form.get('marca', ''),
            modelo=request.form.get('modelo', ''),
            estado=request.form['estado'],
            precio=request.form['precio'],
            ubicacion=request.form['ubicacion'], # Temporal
            numero_serie_f=request.form['numero_serie_f'],
            numero_serie_i=request.form['numero_serie_i'],
            observacion=request.form.get('observacion'),  # Puede ser None
            cliente= cliente if cliente else None
        )
        categoria = Categoria.query.get(nuevo_producto.categoria_id)
        categoria.productos += 1
        movimiento = Movimiento(usuario_id=session['user_id'],acción=f"Añadió el producto {nuevo_producto.numero} de la marca {nuevo_producto.marca}",departamento="Inventario")
        db.session.add(movimiento)
        db.session.add(nuevo_producto)
        db.session.commit()
        print("Producto guardado correctamente")
        return redirect(request.referrer)
    except Exception as e:
        print(f"Error al guardar el producto: {e}")
        return "Error al guardar el producto", 400

# Ruta para añadir cliente
@app.route('/clientes/nuevo', methods=['POST'])
@login_required
def crear_cliente():
    if Cliente.query.filter_by(email=request.form['email']).first() or Cliente.query.filter_by(nombre=request.form['nombre']).first():
        return "El cliente ya existe.", 400
    
    nuevo_cliente = Cliente(
        nombre=request.form['nombre'],
        email=request.form['email'],
        dni=request.form['dni'],
        telefono=request.form['telefono'],
        id_cliente=request.form.get('id_cliente'),  # Cambiado a get para manejar None
        prioridad=request.form['prioridad']
    )
    movimiento = Movimiento(usuario_id=session['user_id'],acción=f"Añadió el cliente {nuevo_cliente.nombre}",departamento="Clientes")
    db.session.add(movimiento)
    db.session.add(nuevo_cliente)
    db.session.commit()
    return redirect(request.referrer)

# Ruta para añadir categoria
@app.route('/categoria/nuevo', methods=['POST'])
@login_required
def crear_categoria():
    nueva_categoria = Categoria(
        nombre=request.form['nombre'],
        descripcion=request.form.get('descripcion')
    )
    db.session.add(nueva_categoria)
    movimiento = Movimiento(usuario_id=session['user_id'],acción=f"Añadió la categoría {nueva_categoria.nombre}",departamento="Categorías")
    db.session.add(movimiento)
    db.session.commit()
    return redirect(request.referrer)
# Ruta para editar inventario
@app.route('/inventario/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_inventario(id):
    inventario = Inventario.query.get_or_404(id)
    if request.method == 'POST':
        inventario.numero = request.form['numero']
        inventario.modelo = request.form['modelo']
        inventario.marca = request.form['marca']
        inventario.estado = request.form['estado']
        inventario.precio = request.form['precio']
        inventario.numero_serie_f = request.form['numero_serie_f']
        inventario.numero_serie_i = request.form['numero_serie_i']
        inventario.ubicacion = request.form['ubicacion']
        inventario.cliente_id = request.form.get('cliente_id')  # Ensure cliente_id is set
        inventario.observacion = request.form.get('observacion')
        inventario.categoria_id = request.form['categoria_id']  # Ensure categoria_id is set
        movimiento = Movimiento(usuario_id=session['user_id'],acción=f"Editó el producto {inventario.numero} de la marca {inventario.marca}",departamento="Inventario")
        db.session.add(movimiento)
        db.session.commit()
        return redirect(url_for('ver_inventario'))
    categorias = Categoria.query.all()
    return render_template('editar_inventario.html', inventario=inventario, categorias=categorias)

# Ruta para editar cliente
@app.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    if request.method == 'POST':
        cliente.nombre = request.form['nombre']
        cliente.email = request.form['email']
        cliente.dni = request.form['dni']
        cliente.telefono = request.form['telefono']
        cliente.prioridad = request.form['prioridad']
        movimiento = Movimiento(usuario_id=session['user_id'],acción=f"Editó el cliente {cliente.nombre}",departamento="Clientes")
        db.session.add(movimiento)
        db.session.commit()
        return redirect(url_for('ver_clientes'))
    return render_template('crear_cliente.html', cliente=cliente)

# Ruta para crear alquiler
@app.route('/alquiler/nuevo', methods=['POST'])
@login_required
def crear_alquiler():
    nuevo_alquiler = Alquiler(
        inventario_id=request.form['inventario_id'],
        cliente_id=request.form['cliente_id'],
        fecha_entrega=datetime.strptime(request.form['fecha_entrega'], '%Y-%m-%d'),
        fecha_recojida=datetime.strptime(request.form['fecha_recojida'], '%Y-%m-%d'),
        estado=request.form['Estado'],  # Nota: Mantuve "Estado" para coincidir con el nombre del campo en el formulario
        precio=request.form['precio']
    )
    db.session.add(nuevo_alquiler)
    movimiento = Movimiento(usuario_id=session['user_id'],acción=f"Añadió el alquiler {nuevo_alquiler.id}",departamento="Alquileres")
    db.session.add(movimiento)
    db.session.commit()
    return redirect(request.referrer)

# Ruta para ver alquileres
@app.route('/alquileres', methods=['GET', 'POST'])
@login_required
def ver_alquileres():
    form = FilterForm()
    
    query = Alquiler.query
    
    if form.validate_on_submit():
        if form.estado.data:
            query = query.filter(Alquiler.estado == form.estado.data)
        if form.fecha_desde.data:
            query = query.filter(Alquiler.fecha_entrega >= form.fecha_desde.data)
        if form.fecha_hasta.data:
            query = query.filter(Alquiler.fecha_entrega <= form.fecha_hasta.data)
    
    alquileres = query.order_by(Alquiler.fecha_entrega.desc()).all()
    clientes = Cliente.query.all()
    inventarios = Inventario.query.all()
    return render_template('alquileres.html', alquileres=alquileres, form=form,clientes=clientes, inventarios=inventarios)

@app.route('/alquileres/<int:id>')
@login_required
def ver_alquiler(id):
    alquiler = Alquiler.query.get_or_404(id)
    return render_template('detalles_alquiler.html', alquiler=alquiler)
@app.template_filter('date_format')
@login_required
def date_format(value):
    if value:
        return value.strftime('%d/%m/%Y')
    return ''

# Ruta para editar alquiler
@app.route('/alquiler/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_alquiler(id):
    alquiler = Alquiler.query.get_or_404(id)
    if request.method == 'POST':
        alquiler.fecha_entrega = datetime.strptime(request.form['fecha_entrega'], '%Y-%m-%d')
        alquiler.fecha_recojida = datetime.strptime(request.form['fecha_recojida'], '%Y-%m-%d')
        alquiler.estado = request.form['Estado'] 
        alquiler.precio = request.form['precio']
        movimiento = Movimiento(usuario_id=session['user_id'],acción=f"Editó el alquiler {alquiler.id}",departamento="Alquileres")
        db.session.add(movimiento)
        db.session.commit()
        return redirect(url_for('ver_alquileres'))
    inventarios = Inventario.query.all()
    clientes = Cliente.query.all()
    return render_template('editar_alquiler.html', alquiler=alquiler, inventarios=inventarios, clientes=clientes)
@app.context_processor
def utility_processor():
        def productos_por_categoria(categoria_id):
            return Inventario.query.filter_by(categoria_id=categoria_id).count()
        return dict(productos_por_categoria=productos_por_categoria)

if __name__ == '__main__':
    with app.app_context():
        #db.drop_all() # CUIDADO esto borra toda la base de datos
        db.create_all()
        Contraseña.create_default_password()
    app.run(host='0.0.0.0', port=5000, debug=True)
