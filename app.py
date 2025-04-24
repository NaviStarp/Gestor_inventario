from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange
import csv
import os
from enum import Enum
from flask import flash
from fpdf import FPDF  # Import the FPDF library
from functools import wraps
from flask import session
from flask_migrate import Migrate
from flask import send_file
# Se crea la instancia de la aplicación Flask
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necesario para usar sesiones

# Base de datos 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventario.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app,db)

# Se crea la tabla Inventario
class Inventario(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, nullable=False)  # Número del inventario
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
    tipo = db.Column(db.String(100), nullable=False)  # tipo del producto

    def __repr__(self):
        return f'<Inventario {self.id}>'


class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255), nullable=True)
    productos = db.Column(db.Integer, nullable=False, default=0)
    
    def __repr__(self):
        return f'<Categoria {self.id}>'
    
class Carrefour_Estado(Enum):
    Disponible = 'Disponible'
    OnTour = 'On Tour'
    NoDisponible = 'No Disponible'    

class Producto_Carrefour(db.Model):
    id = db.Column(db.Integer, primary_key=True,auto_increment=True)
    numero_serie = db.Column(db.String(100), nullable=True)
    numero_serie_i = db.Column(db.String(100), nullable=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(100), nullable=False)
    fecha_entrega = db.Column(db.Date, nullable=True)
    fecha_recojida = db.Column(db.Date, nullable=True)
    estado = db.Column(db.Enum(Carrefour_Estado), nullable=False)
    ubicacion = db.Column(db.String(100), nullable=False)
    observacion = db.Column(db.String(255), nullable=True)

class tipo_movimiento(Enum):
    Añadir = 'Añadir'
    Editar = 'Editar'
    Eliminar = 'Eliminar'

class Movimiento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.relationship('Usuario', backref=db.backref('movimientos', lazy=True))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.now)
    tipo = db.Column(db.Enum(tipo_movimiento), nullable=True)
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
    estado = db.Column(db.String(100), nullable=False) 
    tipo = db.Column(db.Integer, nullable=False)

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
        ('Revisión', 'Revisión'),
        ('Baja', 'Baja')
    ])
    tipo = SelectField('Tipo', choices=[], coerce=str)
    categoria = SelectField('Categoria', choices=[], coerce=int)
    marca = SelectField('Marca', choices=[], coerce=str)
    submit = SubmitField('Filtrar')
    
    def __init__(self, *args, **kwargs):
        super(filtroInventario, self).__init__(*args, **kwargs)
        
        # Limpiar las opciones de los campos SelectField para evitar duplicaciones
        self.tipo.choices = [(0, 'Todos')]
        self.categoria.choices = [(0, 'Todas')]
        self.marca.choices = [(0, 'Todas')]

        # Consultar las marcas de Inventario
        marcasQ = Inventario.query.order_by(Inventario.marca).distinct(Inventario.marca).all()
        marcas = [(marca.marca, marca.marca) for marca in marcasQ]

        # Consultar los tipos de Inventario
        tiposQ = Inventario.query.order_by(Inventario.tipo).distinct(Inventario.tipo).all()
        tipos = [(tipo.tipo, tipo.tipo) for tipo in tiposQ]

        # Asignar las opciones a los campos SelectField
        self.marca.choices = list(set(marcas))  # Sobrescribir las opciones para evitar duplicados
        self.tipo.choices = list(set(tipos))  # Sobrescribir las opciones para evitar duplicados
        self.tipo.choices.insert(0, ('0', 'Todos'))  # Agregar la opción "Todos" al principio
        self.marca.choices.insert(0, (0, 'Todas'))  # Agregar la opción "Todas" al principio
        # Agregar las categorías desde la base de datos
        self.categoria.choices += [(categoria.id, categoria.nombre) for categoria in Categoria.query.all()]


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
    productos_carrefour = Producto_Carrefour.query.all()
    return render_template('index.html', alquileres=alquileres, categorias=categorias, clientes=clientes, inventarios=inventarios,productos_carrefour=productos_carrefour)
@app.route('/movimientos')
@login_required
def movimientos():
    movimientos = Movimiento.query.join(Usuario).filter(Usuario.nombre != 'Dummy', Usuario.nombre != ' Dummy ').all()
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
            # Verificar la contraseña de administrador
            # Si la contraseña de administrador no está vacía
            # y se proporciona una contraseña en el formulario
            # y coincide con la contraseña de administrador
            # entonces se permite el registro
            # de un nuevo usuario
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
    movimiento = Movimiento(usuario_id=session['user_id'],tipo=tipo_movimiento.Editar,acción=f"Editó la categoría {categoria.nombre}",departamento="Categorías")
    db.session.add(movimiento)
    db.session.commit()
    return redirect(request.referrer)

@app.route('/categoria/eliminar/<int:id>', methods=['GET','POST'])
@login_required
def eliminar_categoria(id):
    Inventario.query.filter_by(categoria_id=id).delete()
    categoria = Categoria.query.get_or_404(id)
    movimiento = Movimiento(usuario_id=session['user_id'],tipo=tipo_movimiento.Eliminar,acción=f"Eliminó la categoría {categoria.nombre}",departamento="Categorías")
    db.session.add(movimiento)
    db.session.delete(categoria)
    db.session.commit()
    return redirect(request.referrer)

@app.route('/cliente/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    db.session.delete(cliente)
    movimiento = Movimiento(usuario_id=session['user_id'],tipo=tipo_movimiento.Eliminar,acción=f"Eliminó el cliente {cliente.nombre}",departamento="Clientes")
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

@app.route('/carrefour', methods=['GET'])
@login_required
def ver_carrefour():
    productos = Producto_Carrefour.query.all()
    return render_template('carrefour.html', productos=productos)

@app.route('/carrefour/nuevo', methods=['POST'])
@login_required
def crear_producto_carrefour():
    fecha_entrega = request.form['fecha_entrega']
    fecha_recojida = request.form['fecha_recojida']
    if request.form['fecha_entrega'] == '':
        fecha_entrega = None
    if request.form['fecha_recojida'] == '':
        fecha_recojida = None
    
    nuevo_producto = Producto_Carrefour(
        numero_serie=request.form['numero_serie_f'],
        numero_serie_i=request.form['numero_serie_i'],
        nombre=request.form['nombre'],
        tipo=request.form['tipo'],
        fecha_entrega=datetime.strptime(fecha_entrega, '%Y-%m-%d') if request.form['fecha_entrega'] else None,
        fecha_recojida=datetime.strptime(fecha_recojida, '%Y-%m-%d') if request.form['fecha_recojida'] else None,
        estado=request.form['estado'],
        ubicacion=request.form['ubicacion'],
        observacion=request.form.get('observacion')
    )
    db.session.add(nuevo_producto)
    movimiento = Movimiento(usuario_id=session['user_id'],tipo=tipo_movimiento.Añadir,acción=f"Añadió el producto Carrefour {nuevo_producto.nombre}",departamento="Carrefour")
    db.session.add(movimiento)
    db.session.commit()
    return redirect(request.referrer)

@app.route('/carrefour/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_producto_carrefour(id):
    producto = Producto_Carrefour.query.get_or_404(id)
    if request.method == 'POST':
        fecha_entrega = request.form['fecha_entrega']
        fecha_recojida = request.form['fecha_recojida']
        if request.form['fecha_entrega'] == '':
           fecha_entrega = None
        if request.form['fecha_recojida'] == '':
            fecha_recojida = None
        producto.numero_serie = request.form['numero_serie_f']
        producto.numero_serie_i = request.form['numero_serie_i']
        producto.nombre = request.form['nombre']
        producto.tipo = request.form['tipo']
        producto.fecha_entrega = datetime.strptime(fecha_entrega, '%Y-%m-%d') if fecha_entrega else None
        producto.fecha_recojida = datetime.strptime(fecha_recojida, '%Y-%m-%d') if fecha_recojida else None
        producto.estado = request.form['estado']
        producto.ubicacion = request.form['ubicacion']
        producto.observacion = request.form.get('observacion')
        movimiento = Movimiento(usuario_id=session['user_id'],tipo=tipo_movimiento.Editar,acción=f"Editó el producto Carrefour {producto.nombre}",departamento="Carrefour")
        db.session.add(movimiento)
        db.session.commit()
        return redirect(url_for('ver_carrefour'))
    return render_template(request.referrer, producto=producto)

@app.route('/carrefour/editar_campo/<int:id>', methods=['POST'])
@login_required
def editar_campo_producto_carrefour(id):
    try:
        producto = Producto_Carrefour.query.get_or_404(id)
        data = request.get_json()
        
        if not data:
            return "No se recibieron datos JSON", 400

        campo = data.get('campo')
        valor = data.get('valor')

        if not campo:
            return "Campo no proporcionado", 400
        
        if valor is None:
            return "Valor no proporcionado", 400

        # Verificar que el campo existe en el modelo
        if hasattr(producto, campo):
            # Manejo especial para campos enum
            if campo == 'estado':
                if valor == 'Disponible':
                    producto.estado = Carrefour_Estado.Disponible
                elif valor == 'OnTour':
                    producto.estado = Carrefour_Estado.OnTour
                elif valor == 'NoDisponible':
                    producto.estado = Carrefour_Estado.NoDisponible
                else:
                    return f"Valor no válido para el campo estado: {valor}", 400
            else:
                setattr(producto, campo, valor)
            
            # Guardar el movimiento
            movimiento = Movimiento(
                usuario_id=session['user_id'],
                tipo=tipo_movimiento.Editar,
                acción=f"Editó el campo {campo} del producto Carrefour {producto.nombre}",
                departamento="Carrefour"
            )
            db.session.add(movimiento)
            db.session.commit()
            return "Campo actualizado correctamente", 200
        else:
            return f"Campo no válido: {campo}", 400
    except Exception as e:
        db.session.rollback()
        print(f"Error al actualizar el campo: {e}")
        return f"Error al actualizar: {str(e)}", 500

@app.route('/producto/actualizar/<int:id>', methods=['POST'])
@login_required
def actualizar_producto(id):
    producto = Inventario.query.get_or_404(id)
    data = request.get_json()
    if not data:
        return "No se recibieron datos JSON", 400

    campo = data.get('campo')
    valor = data.get('valor')

    if hasattr(producto, campo):
        try:
            setattr(producto, campo, valor)
            db.session.commit()
            movimiento = Movimiento(usuario_id=session['user_id'], tipo=tipo_movimiento.Editar, acción=f"Actualizó el campo {campo} del producto {producto.numero}", departamento="Inventario")
            db.session.add(movimiento)
            db.session.commit()
            return "Producto actualizado correctamente", 200
        except Exception as e:
            db.session.rollback()
            print(f"Error al actualizar el campo {campo}: {e}")
            return "Error al actualizar el producto", 500
    else:
        return "Campo no válido", 400

@app.route('/carrefour/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_producto_carrefour(id):
    producto = Producto_Carrefour.query.get_or_404(id)
    db.session.delete(producto)
    movimiento = Movimiento(usuario_id=session['user_id'],tipo=tipo_movimiento.Eliminar,acción=f"Eliminó el producto Carrefour {producto.nombre}",departamento="Carrefour")
    db.session.add(movimiento)
    db.session.commit()
    return redirect(request.referrer)

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
    movimiento = Movimiento(usuario_id=session['user_id'],tipo=tipo_movimiento.Eliminar,acción=f"Eliminó el producto {inventario.numero}",departamento="Inventario")
    db.session.add(movimiento)
    db.session.commit()
    return redirect(request.referrer)

@app.route('/alquiler/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_alquiler(id):
    alquiler = Alquiler.query.get_or_404(id)
    db.session.delete(alquiler)
    movimiento = Movimiento(usuario_id=session['user_id'],tipo=tipo_movimiento.Eliminar,acción=f"Eliminó el alquiler {alquiler.id}",departamento="Alquileres")
    db.session.add(movimiento)
    db.session.commit()
    return redirect(request.referrer)

# Ruta para ver inventario
@app.route('/inventario', methods=['GET', 'POST'])
@login_required
def ver_inventario():
    form = filtroInventario()
    
    # Iniciar con la consulta base
    query = Inventario.query.order_by(Inventario.categoria_id,Inventario.tipo,Inventario.marca, Inventario.numero)
    # Procesar el formulario solo si se envía como POST
    if request.method == 'POST' and form.validate():
        if form.estado.data:
            query = query.filter(Inventario.estado == form.estado.data)
        if form.tipo.data and form.tipo.data != '0':  # Evitar filtrar cuando se selecciona "Todos"
            query = query.filter(Inventario.tipo == form.tipo.data)
        if form.categoria.data and form.categoria.data != 0:  # Evitar filtrar cuando se selecciona "Todas"
            query = query.filter(Inventario.categoria_id == form.categoria.data)
        if form.marca.data and form.marca.data != '0':
            query = query.filter(Inventario.marca == form.marca.data)            
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

    # Iniciar con la consulta base
    query = Inventario.query.order_by(
        Inventario.categoria_id, 
        Inventario.tipo, 
        Inventario.marca, 
        Inventario.modelo,
        Inventario.numero
    )
    # Procesar el formulario solo si se envía como POST
    if form.estado.data:
        print("Filtrando por estado ", form.estado.data)
        query = query.filter(Inventario.estado == form.estado.data)
    if form.tipo.data and form.tipo.data != '0':  # Evitar filtrar cuando se selecciona "Todos"
        query = query.filter(Inventario.tipo == form.tipo.data)
    if form.categoria.data and form.categoria.data != 0:  # Evitar filtrar cuando se selecciona "Todas"
        query = query.filter(Inventario.categoria_id == form.categoria.data)
    if form.marca.data and form.marca.data != '0':
        query = query.filter(Inventario.marca == form.marca.data)
    
    # Ejecutar la consulta final
    inventarios = query.all()
    print(inventarios)
    print(form.estado.data, form.tipo.data, form.categoria.data, form.marca.data)
    categorias = Categoria.query.filter(Categoria.id == id).all()
    
    return render_template('inventario.html', categoria=categoria, categorias=categorias,inventarios=inventarios, form=form,es_categoria=True)

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
                    estado = 'Disponible'
                    if row[4] == 'OPERATIVO':
                        estado = 'Disponible'
                    elif row[4] == 'ON TOUR':
                        estado = 'En uso'
                    elif row[4] == 'NO OPERATIVO':
                        estado = 'Baja'
                    elif row[4] == 'REVISION':
                        estado = 'Reparación'
                    try:
                        nuevo_producto = Inventario(
                            numero=row[0] if row[0] else 0,
                            categoria_id=1,  # Default
                            marca=row[2] if row[2] else '',
                            modelo=row[3] if row[3] else '',    
                            estado=estado,
                            ubicacion=row[5] if row[5] else '',
                            observacion=row[6] if row[6] else '',
                            numero_serie_f=row[7] if row[7] else '',
                            numero_serie_i=row[8] if row[8] else '',
                            tipo=row[9] if row[9] else '',
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
                    movimiento = Movimiento(usuario_id=session['user_id'],tipo=tipo_movimiento.Añadir,acción=f"Importó {filas_procesadas} productos",departamento="Inventario")
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
    
@app.route('/inventario/exportar/pdf', methods=['GET'])
@login_required
def exportar_inventario_pdf():
    pdf = FPDF()
    pdf.add_page('L')  # Landscape orientation

    colores_estados = {
        'Disponible': (144, 238, 144),
        'En uso': (135, 206, 250),
        'Baja': (255, 160, 122),
        'Revisión': (255, 255, 153)
    }

    pdf.set_font("Arial", 'B', 16)
    pdf.set_fill_color(70, 130, 180)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 15, "SONIMITAR INVENTARIO", ln=True, align='C', fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 8, "Leyenda de Estados:", 0, 1, 'C')

    # Centrar leyenda
    leyenda_width = len(colores_estados) * 60
    page_width = 297
    start_x = (page_width - leyenda_width) / 2
    y_leyenda = pdf.get_y()
    pdf.set_xy(start_x, y_leyenda)
    pdf.set_x(pdf.get_x() + 20)
    for estado, color in colores_estados.items():
        pdf.set_fill_color(*color)
        pdf.rect(pdf.get_x(), pdf.get_y(), 5, 5, 'F')
        pdf.set_xy(pdf.get_x() + 8, pdf.get_y())
        pdf.cell(40, 5, estado, 0, 0, 'L')
        pdf.set_xy(pdf.get_x() + 10, y_leyenda)
    pdf.ln(16)

    # Definir columnas
    col_widths = {
        'id': 15, 'numero': 20, 'marca': 25, 'modelo': 30, 
        'estado': 20, 'ubicacion': 25, 'serie_f': 30, 'serie_i': 30, 
        'categoria': 25, 'cliente': 20, 'tipo': 20, 'observacion': 40
    }

    tabla_width = sum([
        col_widths['id'], col_widths['numero'], col_widths['marca'],
        col_widths['modelo'], col_widths['tipo'], col_widths['estado'],
        col_widths['ubicacion'], col_widths['serie_f'], col_widths['serie_i']
    ])
    start_x = (page_width - tabla_width) / 2
    pdf.set_x(start_x)

    pdf.set_fill_color(40, 80, 120)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 9)

    headers = ['id', 'numero', 'marca', 'modelo', 'tipo', 'estado', 'ubicacion', 'serie_f', 'serie_i']
    for key in headers:
        label = {
            'id': 'ID', 'numero': 'Número', 'marca': 'Marca', 'modelo': 'Modelo',
            'tipo': 'Tipo', 'estado': 'Estado', 'ubicacion': 'Ubicación',
            'serie_f': 'Serie Fabricante', 'serie_i': 'Serie Interna'
        }[key]
        pdf.cell(col_widths[key], 10, label, 1, 0, 'C', fill=True)
    pdf.ln()

    pdf.set_text_color(0, 0, 0)

    inventarios = Inventario.query.order_by(Inventario.categoria,Inventario.marca,Inventario.modelo,Inventario.numero).all()

    for item in inventarios:
        pdf.set_x(start_x)
        pdf.set_fill_color(245, 245, 245)

        estado_color = colores_estados.get(item.estado, (200, 200, 200))
        categoria_nombre = item.categoria.nombre if item.categoria else "N/A"
        cliente_nombre = Cliente.query.get(item.cliente).nombre if item.cliente else "N/A"

        pdf.cell(col_widths['id'], 10, str(item.id), 1, 0, 'C', fill=True)
        pdf.cell(col_widths['numero'], 10, str(item.numero), 1, 0, 'C', fill=True)
        pdf.cell(col_widths['marca'], 10, item.marca, 1, 0, 'C', fill=True)
        pdf.cell(col_widths['modelo'], 10, item.modelo, 1, 0, 'C', fill=True)
        pdf.cell(col_widths['tipo'], 10, item.tipo, 1, 0, 'C', fill=True)

        pdf.set_fill_color(*estado_color)
        pdf.cell(col_widths['estado'], 10, item.estado, 1, 0, 'C', fill=True)
        pdf.set_fill_color(245, 245, 245)

        pdf.cell(col_widths['ubicacion'], 10, item.ubicacion, 1, 0, 'C', fill=True)
        pdf.cell(col_widths['serie_f'], 10, item.numero_serie_f, 1, 0, 'C', fill=True)
        pdf.cell(col_widths['serie_i'], 10, item.numero_serie_i, 1, 1, 'C', fill=True)

        pdf.set_x(start_x)
        pdf.set_fill_color(250, 250, 250)

        pdf.set_font("Arial", 'B', 8)
        pdf.cell(col_widths['id'], 10, 'Categoría:', 1, 0, 'R', fill=True)
        pdf.cell(col_widths['numero'] + col_widths['marca'], 10, categoria_nombre, 1, 0, 'L', fill=True)

        pdf.set_font("Arial", 'B', 8)
        pdf.cell(col_widths['modelo'], 10, 'Cliente:', 1, 0, 'R', fill=True)
        pdf.cell(col_widths['tipo'] + col_widths['estado'], 10, cliente_nombre, 1, 0, 'L', fill=True)

        pdf.set_font("Arial", 'B', 8)
        pdf.cell(col_widths['ubicacion'], 10, 'Observación:', 1, 0, 'R', fill=True)
        observacion_text = item.observacion if item.observacion else "Sin observaciones"
        pdf.cell(col_widths['serie_f'] + col_widths['serie_i'], 10, observacion_text, 1, 1, 'L', fill=True)

        pdf.ln(3)

    pdf.ln(15)
    pdf.set_font("Arial", 'I', 8)
    from datetime import datetime
    pdf.cell(0, 10, f"Reporte generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 0, 1, 'R')

    pdf_path = "inventario.pdf"
    pdf.output(pdf_path)
    return send_file(pdf_path, as_attachment=True, download_name="Inventario.pdf")

    
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
            tipo=request.form['tipo'],
            ubicacion=request.form['ubicacion'], # Temporal
            numero_serie_f=request.form['numero_serie_f'],
            numero_serie_i=request.form['numero_serie_i'],
            observacion=request.form.get('observacion'),  # Puede ser None
            cliente= cliente if cliente else None
        )
        categoria = Categoria.query.get(nuevo_producto.categoria_id)
        categoria.productos += 1
        movimiento = Movimiento(usuario_id=session['user_id'],tipo=tipo_movimiento.Añadir,acción=f"Añadió el producto {nuevo_producto.numero} de la marca {nuevo_producto.marca}",departamento="Inventario")
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
    movimiento = Movimiento(usuario_id=session['user_id'],tipo=tipo_movimiento.Añadir,acción=f"Añadió el cliente {nuevo_cliente.nombre}",departamento="Clientes")
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
    movimiento = Movimiento(usuario_id=session['user_id'],tipo=tipo_movimiento.Añadir,acción=f"Añadió la categoría {nueva_categoria.nombre}",departamento="Categorías")
    db.session.add(movimiento)
    db.session.commit()
    return redirect(request.referrer)
# Ruta para editar inventario
@app.route('/inventario/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_inventario(id):
    inventario = Inventario.query.get_or_404(id)
    if request.method == 'POST':
        print("Datos recibidos:", request.data)
        print("Datos del formulario:", request.form)
        try:
            # Intentar obtener datos JSON
            data = request.get_json()
        except Exception as e:
            print(f"Error al obtener datos JSON: {e}")
            data = None

        # Si no se reciben datos JSON, usar datos del formulario
        if not data:
            data = request.form

        inventario.numero = data.get('numero', inventario.numero)
        inventario.modelo = data.get('modelo', inventario.modelo)
        inventario.marca = data.get('marca', inventario.marca)
        inventario.estado = data.get('estado', inventario.estado)
        inventario.tipo = data.get('tipo', inventario.tipo)
        inventario.numero_serie_f = data.get('numero_serie_f', inventario.numero_serie_f)
        inventario.numero_serie_i = data.get('numero_serie_i', inventario.numero_serie_i)
        inventario.ubicacion = data.get('ubicacion', inventario.ubicacion)
        inventario.cliente = data.get('cliente_id', inventario.cliente)
        inventario.observacion = data.get('observacion', inventario.observacion)
        inventario.categoria_id = data.get('categoria_id', inventario.categoria_id)

        print(inventario.categoria_id, inventario.numero, inventario.marca, inventario.modelo, inventario.estado, inventario.tipo, inventario.numero_serie_f, inventario.numero_serie_i, inventario.ubicacion, inventario.cliente, inventario.observacion)
        movimiento = Movimiento(usuario_id=session['user_id'], tipo=tipo_movimiento.Editar, acción=f"Editó el producto {inventario.numero} de la marca {inventario.marca}", departamento="Inventario")
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
        movimiento = Movimiento(usuario_id=session['user_id'],tipo=tipo_movimiento.Editar,acción=f"Editó el cliente {cliente.nombre}",departamento="Clientes")
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
        tipo=request.form['tipo']
    )
    db.session.add(nuevo_alquiler)
    movimiento = Movimiento(usuario_id=session['user_id'],tipo=tipo_movimiento.Añadir,acción=f"Añadió el alquiler {nuevo_alquiler.id}",departamento="Alquileres")
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
        alquiler.tipo = request.form['tipo']
        movimiento = Movimiento(usuario_id=session['user_id'],tipo=tipo_movimiento.Editar,acción=f"Editó el alquiler {alquiler.id}",departamento="Alquileres")
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
        produtos = Inventario.query.filter_by(estado='Reparación').all() # TEMPORAL
        for produto in produtos: # TEMPORAL
            produto.estado = 'Revisión' # TEMPORAL
            db.session.commit() # TEMPORAL
        inventarios = Inventario.query.all()
        for inventario in inventarios:
            print(isinstance(inventario.numero, str))
            if isinstance(inventario.numero, str):  # Si es una cadena
                inventario.numero = int(inventario.numero)  # Convertir a entero
        Contraseña.create_default_password()

    app.run(host='0.0.0.0', port=80, debug=True)
