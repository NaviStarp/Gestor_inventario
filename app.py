from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange
# Se crea la instancia de la aplicación Flask
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necesario para usar sesiones

# Base de datos 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventario.db'  # Cambia esto según tu base de datos
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Se crea la tabla Inventario
class Inventario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=True)
    cliente = db.relationship('Cliente', backref=db.backref('inventarios', lazy=True))
    estado = db.Column(db.String(100), nullable=False)
    
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id', ondelete='CASCADE'), nullable=False)  # <- Asegurar la clave foránea
    categoria = db.relationship('Categoria', backref=db.backref('inventarios', lazy=True))  # <- Definir la relación correctamente
    
    precio = db.Column(db.Integer, nullable=False) 
    numero_serie_f = db.Column(db.String(100), nullable=False)  # Numero de serie del fabricante
    numero_serie_i = db.Column(db.String(100), nullable=False)  # Numero de serie interno
    observaciones = db.Column(db.String(255), nullable=True)  # Observaciones opcionales

    def __repr__(self):
        return f'<Inventario {self.id}>'


class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255), nullable=True)
    
    def __repr__(self):
        return f'<Categoria {self.id}>'

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

# Ruta de inicio
@app.route('/')
def inicio():
    categorias = Categoria.query.all()
    clientes = Cliente.query.all()
    inventarios = Inventario.query.all()
    alquileres = Alquiler.query.all()
    return render_template('index.html', alquileres=alquileres, categorias=categorias, clientes=clientes, inventarios=inventarios)

@app.route('/categoria/editar', methods=['POST'])
def editar_categoria():
    categoria = Categoria.query.get_or_404(request.form['id'])
    categoria.nombre = request.form['nombre']
    categoria.descripcion = request.form.get('descripcion')
    db.session.commit()
    return redirect(url_for('inicio'))

@app.route('/categoria/eliminar/<int:id>', methods=['POST'])
def eliminar_categoria(id):
    Inventario.query.filter_by(categoria_id=id).delete()
    categoria = Categoria.query.get_or_404(id)
    db.session.delete(categoria)
    db.session.commit()
    return redirect(url_for('inicio'))

@app.route('/cliente/eliminar/<int:id>', methods=['POST'])
def eliminar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    db.session.delete(cliente)
    db.session.commit()
    return redirect(url_for('inicio'))
@app.route('/categorias/')
def ver_categorias():
    categorias = Categoria.query.all()
    return render_template('categorias.html', categorias=categorias)

@app.route('/inventario/eliminar/<int:id>', methods=['POST'])
def eliminar_producto(id):
    inventario = Inventario.query.get_or_404(id)
    db.session.delete(inventario)
    db.session.commit()
    return redirect(url_for('inicio'))

@app.route('/alquiler/eliminar/<int:id>', methods=['POST'])
def eliminar_alquiler(id):
    alquiler = Alquiler.query.get_or_404(id)
    db.session.delete(alquiler)
    db.session.commit()
    return redirect(url_for('inicio'))

# Ruta para ver inventario
@app.route('/inventario')
def ver_inventario():
    inventarios = Inventario.query.all()
    return render_template('inventario.html', inventarios=inventarios)
#Ruta para ver productos de una categoria
@app.route('/categoria/<int:id>')
def ver_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    inventarios = Inventario.query.filter_by(categoria_id=id).all()
    return render_template('inventario.html', categoria=categoria, inventarios=inventarios)

# Ruta para ver clientes
@app.route('/clientes')
def ver_clientes():
    clientes = Cliente.query.all()
    return render_template('clientes.html', clientes=clientes)

# Ruta para añadir producto al inventario
@app.route('/inventario/nuevo', methods=['POST'])
def crear_producto():
    nuevo_producto = Inventario(
        cliente_id=request.form['cliente_id'],
        estado=request.form['estado'],
        precio=request.form['precio'],
        categoria_id=request.form['categoria_id'],
        numero_serie_f=request.form['numero_serie_f'],
        numero_serie_i=request.form['numero_serie_i'],
        observaciones=request.form.get('observaciones')
    )
    db.session.add(nuevo_producto)
    db.session.commit()
    return redirect(url_for('inicio'))

# Ruta para añadir cliente
@app.route('/clientes/nuevo', methods=['POST'])
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
    db.session.add(nuevo_cliente)
    db.session.commit()
    return redirect(url_for('inicio'))

# Ruta para añadir categoria
@app.route('/categoria/nuevo', methods=['POST'])
def crear_categoria():
    nueva_categoria = Categoria(
        nombre=request.form['nombre'],
        descripcion=request.form.get('descripcion')
    )
    db.session.add(nueva_categoria)
    db.session.commit()
    return redirect(url_for('inicio'))

# Ruta para editar inventario
@app.route('/inventario/editar/<int:id>', methods=['GET', 'POST'])
def editar_inventario(id):
    inventario = Inventario.query.get_or_404(id)
    if request.method == 'POST':
        inventario.estado = request.form['estado']
        inventario.precio = request.form['precio']
        inventario.numero_serie_f = request.form['numero_serie_f']
        inventario.numero_serie_i = request.form['numero_serie_i']
        inventario.observaciones = request.form.get('observaciones')
        inventario.categoria_id = request.form['categoria_id']  # Ensure categoria_id is set
        db.session.commit()
        return redirect(url_for('ver_inventario'))
    categorias = Categoria.query.all()
    return render_template('editar_inventario.html', inventario=inventario, categorias=categorias)

# Ruta para editar cliente
@app.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    if request.method == 'POST':
        cliente.nombre = request.form['nombre']
        cliente.email = request.form['email']
        cliente.dni = request.form['dni']
        cliente.telefono = request.form['telefono']
        cliente.prioridad = request.form['prioridad']
        db.session.commit()
        return redirect(url_for('ver_clientes'))
    return render_template('crear_cliente.html', cliente=cliente)

# Ruta para crear alquiler
@app.route('/alquiler/nuevo', methods=['POST'])
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
    db.session.commit()
    return redirect(url_for('inicio'))

# Ruta para ver alquileres
@app.route('/alquileres', methods=['GET', 'POST'])
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
    
    return render_template('alquileres.html', alquileres=alquileres, form=form)

@app.route('/alquileres/<int:id>')
def ver_alquiler(id):
    alquiler = Alquiler.query.get_or_404(id)
    return render_template('detalles_alquiler.html', alquiler=alquiler)
@app.template_filter('date_format')
def date_format(value):
    if value:
        return value.strftime('%d/%m/%Y')
    return ''

# Ruta para editar alquiler
@app.route('/alquiler/editar/<int:id>', methods=['GET', 'POST'])
def editar_alquiler(id):
    alquiler = Alquiler.query.get_or_404(id)
    if request.method == 'POST':
        alquiler.fecha_entrega = datetime.strptime(request.form['fecha_entrega'], '%Y-%m-%d')
        alquiler.fecha_recojida = datetime.strptime(request.form['fecha_recojida'], '%Y-%m-%d')
        alquiler.estado = request.form['Estado']  # Nota: Mantuve "Estado" para coincidir con el nombre del campo en el formulario
        alquiler.precio = request.form['precio']
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
       # db.drop_all() # CUIDADO esto borra toda la base de datos
        db.create_all()
    app.run(debug=True)