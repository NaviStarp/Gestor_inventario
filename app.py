from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# Se crea la instancia de la aplicaciÃ³n Flask
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necesario para usar sesiones
# Base de datos 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Se crea la tabla Inventario
class Inventario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    cliente = db.relationship('Cliente', backref=db.backref('inventarios', lazy=True))
    estado = db.Column(db.String(100), nullable=False)
    precio= db.Column(db.Integer, nullable=False) 
    numero_serie_f = db.Column(db.String(100), nullable=False)  # Numero de serie del fabricante
    numero_serie_i = db.Column(db.String(100), nullable=False)  # Numero de serie internogit 
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
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)  # Quien crea la tarea
    nombre_usuario = db.relationship('Usuario', backref=db.backref('tareas', lazy=True))
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

    def __repr__(self):
        return f'<Alquiler {self.id}>'
