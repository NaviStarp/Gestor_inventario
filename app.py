from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    cliente = db.relationship('Cliente', backref=db.backref('inventarios', lazy=True))
    estado = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Integer, nullable=False) 
    numero_serie_f = db.Column(db.String(100), nullable=False)  # Numero de serie del fabricante
    numero_serie_i = db.Column(db.String(100), nullable=False)  # Numero de serie interno
    observaciones = db.Column(db.String(255), nullable=True)  # Observaciones opcionales

    def __repr__(self):
        return f'<Inventario {self.id}>'

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

# Ruta de inicio
@app.route('/')
def inicio():
    return render_template('index.html')

# Ruta para ver inventario
@app.route('/inventario')
def ver_inventario():
    inventarios = Inventario.query.all()
    return render_template('inventario.html', inventarios=inventarios)

# Ruta para ver clientes
@app.route('/clientes')
def ver_clientes():
    clientes = Cliente.query.all()
    return render_template('clientes.html', clientes=clientes)

# Ruta para añadir producto al inventario
@app.route('/inventario/nuevo', methods=['GET', 'POST'])
def crear_producto():
    if request.method == 'POST':
        nuevo_producto = Inventario(
            cliente_id=request.form['cliente_id'],
            estado=request.form['estado'],
            precio=request.form['precio'],
            numero_serie_f=request.form['numero_serie_f'],
            numero_serie_i=request.form['numero_serie_i'],
            observaciones=request.form.get('observaciones')
        )
        db.session.add(nuevo_producto)
        db.session.commit()
        return redirect(url_for('ver_inventario'))
    clientes = Cliente.query.all()
    return render_template('crear_producto.html', clientes=clientes)

# Ruta para añadir cliente
@app.route('/clientes/nuevo', methods=['GET', 'POST'])
def crear_cliente():
    if request.method == 'POST':
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
        return redirect(url_for('ver_clientes'))
    return render_template('añadir_cliente.html')

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
        db.session.commit()
        return redirect(url_for('ver_inventario'))
    return render_template('editar_inventario.html', inventario=inventario)

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
@app.route('/alquiler/nuevo', methods=['GET', 'POST'])
def crear_alquiler():
    if request.method == 'POST':
        nuevo_alquiler = Alquiler(
            inventario_id=request.form['inventario_id'],
            cliente_id=request.form['cliente_id'],
            fecha_entrega=datetime.strptime(request.form['fecha_entrega'], '%Y-%m-%d'),
            fecha_recojida=datetime.strptime(request.form['fecha_recojida'], '%Y-%m-%d'),
            estado=request.form['estado'],  # Corregido: Era "Estado" (inconsistente)
            precio=request.form['precio']
        )
        db.session.add(nuevo_alquiler)
        db.session.commit()
        return redirect(url_for('ver_alquileres'))
    inventarios = Inventario.query.all()
    clientes = Cliente.query.all()
    return render_template('crear_alquiler.html', inventarios=inventarios, clientes=clientes)

# Ruta para ver alquileres
@app.route('/alquileres')
def ver_alquileres():
    alquileres = Alquiler.query.all()
    return render_template('alquileres.html', alquileres=alquileres)

# Ruta para editar alquiler
@app.route('/alquiler/editar/<int:id>', methods=['GET', 'POST'])
def editar_alquiler(id):
    alquiler = Alquiler.query.get_or_404(id)
    if request.method == 'POST':
        alquiler.fecha_entrega = datetime.strptime(request.form['fecha_entrega'], '%Y-%m-%d')
        alquiler.fecha_recojida = datetime.strptime(request.form['fecha_recojida'], '%Y-%m-%d')
        alquiler.estado = request.form['estado']  # Corregido: Era "Estado" (inconsistente)
        alquiler.precio = request.form['precio']
        db.session.commit()
        return redirect(url_for('ver_alquileres'))
    inventarios = Inventario.query.all()
    clientes = Cliente.query.all()
    return render_template('editar_alquiler.html', alquiler=alquiler, inventarios=inventarios, clientes=clientes)

if __name__ == '__main__':
    app.run(debug=True)
