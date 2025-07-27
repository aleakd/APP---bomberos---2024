from flask import Flask, render_template, request, redirect, url_for, flash, jsonify,send_from_directory, abort,send_file
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from functools import wraps
import pytz
from sqlalchemy import func
from sqlalchemy import text, extract, desc
from sqlalchemy import  Enum as SqlEnum
import enum
from collections import Counter
from werkzeug.middleware.proxy_fix import ProxyFix
from pytz import timezone
import os
from werkzeug.utils import secure_filename
from datetime import datetime, date, timedelta
from fpdf import FPDF

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}



app = Flask(__name__)
app.config['TIMEZONE'] = pytz.timezone('America/Argentina/Buenos_Aires')
app.config['SECRET_KEY'] = 'ale14541ale'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bomberoscarlospaz.db'
db = SQLAlchemy(app)


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'  # Vista para login

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.template_filter('replace_backslash')
def replace_backslash(value):
    return value.replace('\\', '/')

app.jinja_env.filters['replace_backslash'] = replace_backslash




#----------------------------------------------#----------------------------------------------

class Bomberos(db.Model):
    legajo_numero = db.Column(db.Integer, primary_key=True, unique=True)
    apellido = db.Column(db.String(100))
    nombre = db.Column(db.String(100))
    dni = db.Column(db.Integer)
    dni_pdf = db.Column(db.String(300))
    telefono = db.Column(db.Integer)
    telefono_alternativo = db.Column(db.Integer)
    fecha_nacimiento = db.Column(db.Date)
    domicilio = db.Column(db.String(300))
    email = db.Column(db.String(100))
    rol = db.Column(db.String(100))
    grupo_sanguineo = db.Column(db.String(100))
    alergia = db.Column(db.String(100))
    camada = db.Column(db.String(10))
    estado= db.Column(db.String(100))
    obra_scocial=db.Column(db.String(10))
    registro = db.Column(db.String(1000))
    nivel_educativo=db.Column(db.String(1000))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    numero_legajo=db.Column(db.Integer)
    telefono = db.Column(db.String(15))
    rol = db.Column(db.String(10), default='usuario')  # Add the role field

class IndumentariaProvista(UserMixin, db.Model):
    numero_legajo = db.Column(db.Integer, primary_key=True)
    gorra = db.Column(db.Integer)
    remera_azul = db.Column(db.Integer)
    pantalon_fajina = db.Column(db.Integer)
    borcegos = db.Column(db.Integer)
    rompeviento = db.Column(db.Integer)
    camp_neopren = db.Column(db.Integer)
    bermuda = db.Column(db.Integer)

class Epp_provisto(UserMixin, db.Model):
    numero_legajo=db.Column(db.Integer, primary_key=True)
    casco_estructural=db.Column(db.Integer)
    monja_estructural=db.Column(db.Integer)
    guantes__estructural=db.Column(db.Integer)
    chaqueton_estructural=db.Column(db.Integer)
    pantalon_estructural=db.Column(db.Integer)
    botas_estructural=db.Column(db.Integer)
    monja_forestal=db.Column(db.Integer)
    camisa_forestal=db.Column(db.Integer)
    guantes_forestal=db.Column(db.Integer)
    pantalon_forestal=db.Column(db.Integer)
    antiparras_forestal=db.Column(db.Integer)
    linterna_forestal=db.Column(db.Integer)

class Cambios_Guardia(UserMixin, db.Model):
    cambio_guardia_id=db.Column(db.Integer, unique=True,primary_key=True)
    numero_legajo=db.Column(db.Integer)
    fecha_solicitud=db.Column(db.Date)
    rango_horario=db.Column(db.Time)
    rango_horario2=db.Column(db.Time)
    legajo_quien_cubre= db.Column(db.Integer)
    motivo=db.Column(db.String(100))
    fecha_devolucion=db.Column(db.Date)
    imagen = db.Column(db.String(300))
    aprovado = db.Column(db.String(300))

class Licencias_Conducir(UserMixin, db.Model):
    numero_legajo=db.Column(db.Integer, primary_key=True)
    tipo= db.Column(db.Integer)
    fecha_otorgacion= db.Column(db.Date)
    fecha_vencimiento = db.Column(db.Date)
    observacion=db.Column(db.String(300))
    lic_frente= db.Column(db.String(300))
    lic_dorso= db.Column(db.String(300))


class Partes_Licencia(UserMixin, db.Model):
    id_licencia=db.Column(db.Integer, primary_key=True)
    numero_legajo=db.Column(db.Integer)
    tipo_licencia = db.Column(db.String(300))
    fecha_solicitud=db.Column(db.Date)
    fecha_inicio_licencia=db.Column(db.Date)
    fecha_fin_licencia=db.Column(db.Date)
    parte_licencia=db.Column(db.String(300))

class Ficha_Medica(UserMixin, db.Model):
    id_ficha_medica=db.Column(db.Integer, primary_key=True)
    numero_legajo = db.Column(db.Integer)
    fecha_ficha = db.Column(db.Date)
    observaciones=db.Column(db.String(300))
    pdf_ficha_medica = db.Column(db.String(300))


class Talles(UserMixin, db.Model):
    numero_legajo = db.Column(db.Integer, primary_key=True)
    remera_fajina = db.Column(db.String(10))
    pantalon_fajina = db.Column(db.Integer)
    campera_fajina= db.Column(db.String(10))
    borcegos = db.Column(db.Integer)

class Aistencia(UserMixin, db.Model):
    id_asistencia = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.Integer)
    tipo_registro = db.Column(db.String(10))
    actividad = db.Column(db.String(30))
    fecha = db.Column(db.Date)
    hora = db.Column(db.String(10))


class ControlAutomotor(UserMixin, db.Model):
    id_control = db.Column(db.Integer, primary_key=True)
    numero_legajo = db.Column(db.Integer)
    nombre_unidad = db.Column(db.String(10))
    fecha = db.Column(db.Date)
    hora = db.Column(db.String(10))
    bateria = db.Column(db.String(10))
    odometro = db.Column(db.Integer)
    combustible = db.Column(db.String(10))
    acite_motor = db.Column(db.String(10))
    agua_radiador = db.Column(db.String(10))
    liq_freno = db.Column(db.String(10))
    neumaticos = db.Column(db.String(10))
    frenos = db.Column(db.String(10))
    direccion = db.Column(db.String(10))
    luces_baja = db.Column(db.String(10))
    luces_alta = db.Column(db.String(10))
    balizas = db.Column(db.String(10))
    estrobos = db.Column(db.String(10))
    sirena = db.Column(db.String(10))
    equipo_base = db.Column(db.String(10))
    limpieza_interior = db.Column(db.String(10))
    limpieza_exterior = db.Column(db.String(10))
    puesta_marcha = db.Column(db.String(10))
    agua_tanque = db.Column(db.String(10))
    observaciones = db.Column(db.String(1000))

class ControlKit(UserMixin, db.Model):
    id_control =db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date)
    hora = db.Column(db.String(10))
    numero_legajo = db.Column(db.Integer)
    nombre_unidad = db.Column(db.String(10))
    nivel_aceite =db.Column(db.String(10))
    combustible = db.Column(db.String(10))
    bidon_nafta = db.Column(db.String(10))
    agua_tanque = db.Column(db.String(10))
    aceite_motor = db.Column(db.String(10))
    marcha = db.Column(db.String(10))
    novedades = db.Column(db.String(1000))


class Centralistas_horarios(UserMixin, db.Model):
    id_asistencia = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.Integer)
    tipo_registro = db.Column(db.String(10))
    fecha = db.Column(db.Date)
    hora = db.Column(db.String(10))




class Salida(db.Model):
    id_salida = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    unidad = db.Column(db.String(50), nullable=False)
    tipo_alarma = db.Column(db.String(100), nullable=False)
    numero_alarma = db.Column(db.Integer)
    a_cargo = db.Column(db.String(100), nullable=False)
    chofer = db.Column(db.String(100), nullable=False)
    dotacion = db.Column(db.Text, nullable=False)
    qth = db.Column(db.String(255), nullable=False)
    operador = db.Column(db.String(100), nullable=False)
    bros_base = db.Column(db.String(100), nullable=False)
    jefe_guardia= db.Column(db.String(100), nullable=False)
    observaciones = db.Column(db.Text)  # Nuevo campo


class Llegada(db.Model):
    __tablename__ = 'llegada'
    id_llegada = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    unidad = db.Column(db.String(10), nullable=False)
    hora_salida = db.Column(db.Time, nullable=False)
    hora_llegada = db.Column(db.Time, nullable=False)
    novedades = db.Column(db.String(500), nullable=True)
    numero_alarma = db.Column(db.Integer)
    a_cargo = db.Column(db.String(100), nullable=True)


class MaterialesR1(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    numero_legajo = db.Column(db.String(10), nullable=False)
    observaciones = db.Column(db.Text, nullable=True)
    cinta_de_vallado = db.Column(db.String(10), nullable=True)
    alcohol_en_gel = db.Column(db.String(10), nullable=True)
    llave_de_ascensor = db.Column(db.String(10), nullable=True)
    herramienta_multiproposito_manual = db.Column(db.String(10), nullable=True)
    bateria_luz = db.Column(db.String(10), nullable=True)
    mapa_vcp = db.Column(db.String(10), nullable=True)
    llave_del_11 = db.Column(db.String(10), nullable=True)
    par_de_guantes_de_rescate = db.Column(db.String(10), nullable=True)
    kit_balizas = db.Column(db.String(10), nullable=True)
    extintor_1k = db.Column(db.String(10), nullable=True)
    tubo_de_oxigeno = db.Column(db.String(10), nullable=True)
    gato = db.Column(db.String(10), nullable=True)
    caja_guantes_nitrilo = db.Column(db.String(10), nullable=True)
    luz_de_escena = db.Column(db.String(10), nullable=True)
    conos = db.Column(db.String(10), nullable=True)
    colcha = db.Column(db.String(10), nullable=True)
    estabilizadores = db.Column(db.String(10), nullable=True)
    bolso_cubre_parantes = db.Column(db.String(10), nullable=True)
    cojinetes_inflables = db.Column(db.String(10), nullable=True)
    consola_de_comando_dual = db.Column(db.String(10), nullable=True)
    bolso_con_las_mangueras = db.Column(db.String(10), nullable=True)
    tubo = db.Column(db.String(10), nullable=True)
    mochila_de_juguetes = db.Column(db.String(10), nullable=True)
    bolso_prehospitalario = db.Column(db.String(10), nullable=True)
    bolso_de_trauma = db.Column(db.String(10), nullable=True)
    bolso_de_parto = db.Column(db.String(10), nullable=True)
    chaleco_extraccion_adulto = db.Column(db.String(10), nullable=True)
    chaleco_extraccion_pediatric = db.Column(db.String(10), nullable=True)
    bolso_de_ferulas_semi_rigidas = db.Column(db.String(10), nullable=True)
    bolso_de_airbag = db.Column(db.String(10), nullable=True)
    valija_de_cubre_airbag = db.Column(db.String(10), nullable=True)
    equipos_de_bioseguridad = db.Column(db.String(10), nullable=True)
    sierra_sable = db.Column(db.String(10), nullable=True)

    techo_escalera = db.Column(db.String(10), nullable=True)
    tablas_espinal_largas = db.Column(db.String(10), nullable=True)
    masa = db.Column(db.String(10), nullable=True)
    hooligans = db.Column(db.String(10), nullable=True)
    trancha_mediana = db.Column(db.String(10), nullable=True)
    cunas = db.Column(db.String(10), nullable=True)
    cuña_escalonada = db.Column(db.String(10), nullable=True)
    tabla_espinal_mediana = db.Column(db.String(10), nullable=True)
    tabla_espinal_chica = db.Column(db.String(10), nullable=True)
    holomatro = db.Column(db.String(10), nullable=True)
    expansor = db.Column(db.String(10), nullable=True)
    multipropósito = db.Column(db.String(10), nullable=True)
    cizalla = db.Column(db.String(10), nullable=True)
    ram = db.Column(db.String(10), nullable=True)
    bolsa_de_aserrin = db.Column(db.String(10), nullable=True)
    barreta_chica = db.Column(db.String(10), nullable=True)
    extintor_5k = db.Column(db.String(10), nullable=True)
    bidon_nafta = db.Column(db.String(10), nullable=True)

class MaterialesB3(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    numero_legajo = db.Column(db.String(10), nullable=False)
    observaciones = db.Column(db.Text, nullable=True)
    camara_termica = db.Column(db.String(10), nullable=True)
    pistola_termica = db.Column(db.String(10), nullable=True)
    reflector_portatil = db.Column(db.String(10), nullable=True)
    cinta_de_vallado = db.Column(db.String(10), nullable=True)
    alcohol_en_gel = db.Column(db.String(10), nullable=True)
    matafuego_5kg = db.Column(db.String(10), nullable=True)
    kit_balizas = db.Column(db.String(10), nullable=True)
    plano_de_vcp = db.Column(db.String(10), nullable=True)
    lanza_nh_2 = db.Column(db.String(10), nullable=True)
    lanzas_nh_1medio = db.Column(db.String(10), nullable=True)
    filtro_manguerote = db.Column(db.String(10), nullable=True)
    llave_stz_manguerote = db.Column(db.String(10), nullable=True)
    llave_nh = db.Column(db.String(10), nullable=True)
    halligan = db.Column(db.String(10), nullable=True)
    era_con_mascara = db.Column(db.String(10), nullable=True)
    y_stz = db.Column(db.String(10), nullable=True)
    conos = db.Column(db.String(10), nullable=True)
    acople_dinnem_stz = db.Column(db.String(10), nullable=True)
    reductor_stz_ww_2medio_a_1medio = db.Column(db.String(10), nullable=True)
    reductor_stz_a_nh_1medio = db.Column(db.String(10), nullable=True)
    reductor_stz_a_nh_1 = db.Column(db.String(10), nullable=True)
    reductor_stz_2_a_stz_1medio = db.Column(db.String(10), nullable=True)
    reductor_stz_2_a_nh_1medio = db.Column(db.String(10), nullable=True)
    reductor_stz_2_a_nh_1 = db.Column(db.String(10), nullable=True)
    reductor_stz_2_a_stz_1 = db.Column(db.String(10), nullable=True)
    acople_din_stz = db.Column(db.String(10), nullable=True)
    acople_stz_a_nh_2 = db.Column(db.String(10), nullable=True)
    llave_stz = db.Column(db.String(10), nullable=True)
    desvanadera = db.Column(db.String(10), nullable=True)
    pertiga = db.Column(db.String(10), nullable=True)
    manguerote = db.Column(db.String(10), nullable=True)
    escalera = db.Column(db.String(10), nullable=True)
    linea_nh_1medio = db.Column(db.String(10), nullable=True)
    linea_nh_2 = db.Column(db.String(10), nullable=True)
    linea_stz_1medio = db.Column(db.String(10), nullable=True)
    linea_stz_2 = db.Column(db.String(10), nullable=True)
    bolso_prehospitalario = db.Column(db.String(10), nullable=True)
    columna_hidrante = db.Column(db.String(10), nullable=True)
    trancha = db.Column(db.String(10), nullable=True)



class ControlBolsoR1(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    numero_legajo = db.Column(db.String(10), nullable=False)
    estado_bolso = db.Column(db.String(10), nullable=False)  # 'OK' o 'X'
    observaciones = db.Column(db.Text, nullable=True)


class ControlBolsoB3(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    numero_legajo = db.Column(db.String(10), nullable=False)
    estado_bolso = db.Column(db.String(10), nullable=False)  # 'OK' o 'X'
    observaciones = db.Column(db.Text, nullable=True)

class MaterialesBF1(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    numero_legajo = db.Column(db.String(10), nullable=False)
    estado_bolso = db.Column(db.String(10), nullable=False)  # 'OK' o 'X'
    colaborador1 = db.Column(db.String(10), nullable=False)
    colaborador2 = db.Column(db.String(10), nullable=False)
    observaciones = db.Column(db.Text, nullable=True)


class MaterialesF2(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    numero_legajo = db.Column(db.String(10), nullable=False)
    estado_materiales = db.Column(db.String(10), nullable=False)  # 'OK' o 'X'
    colaborador1 = db.Column(db.String(10), nullable=False)
    colaborador2 = db.Column(db.String(10), nullable=False)
    observaciones = db.Column(db.Text, nullable=True)

class MaterialesB4(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    numero_legajo = db.Column(db.String(10), nullable=False)
    estado_materiales = db.Column(db.String(10), nullable=False)  # 'OK' o 'X'
    colaborador1 = db.Column(db.String(10), nullable=False)
    colaborador2 = db.Column(db.String(10), nullable=False)
    observaciones = db.Column(db.Text, nullable=True)

class MaterialesB2(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    numero_legajo = db.Column(db.String(10), nullable=False)
    estado_materiales = db.Column(db.String(10), nullable=False)  # 'OK' o 'X'
    colaborador1 = db.Column(db.String(10), nullable=False)
    colaborador2 = db.Column(db.String(10), nullable=False)
    observaciones = db.Column(db.Text, nullable=True)

class Equipamiento_B3(db.Model):
    __tablename__ = 'Equipamiento_B3'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    numero_legajo = db.Column(db.String(10), nullable=False)
    estado_materiales = db.Column(db.String(10), nullable=False)  # 'OK' o 'X'
    colaborador1 = db.Column(db.String(10), nullable=False)
    colaborador2 = db.Column(db.String(10), nullable=False)
    observaciones = db.Column(db.Text, nullable=True)

class Equipamiento_R1(db.Model):
    __tablename__ = 'Equipamiento_R1'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    numero_legajo = db.Column(db.String(10), nullable=False)
    estado_materiales = db.Column(db.String(10), nullable=False)  # 'OK' o 'X'
    colaborador1 = db.Column(db.String(10), nullable=False)
    colaborador2 = db.Column(db.String(10), nullable=False)
    observaciones = db.Column(db.Text, nullable=True)

class EstadoConfirmacion(enum.Enum):
    pendiente = "pendiente"
    confirmado = "confirmado"
    rechazado = "rechazado"

class CambioGuardia(db.Model):
    __tablename__ = 'CambioGuardia'

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    legajo_solicitante = db.Column(db.Integer, nullable=False)
    tipo_solicitud = db.Column(db.Enum('cambio', 'devolucion'), nullable=False)
    motivo = db.Column(db.String(100))
    fecha_ausencia = db.Column(db.Date, nullable=False)
    jefe_guardia = db.Column(db.String(50), nullable=True)
    hora_desde = db.Column(db.Time, nullable=False)
    hora_hasta = db.Column(db.Time, nullable=False)
    legajo_quien_cubre = db.Column(db.Integer, nullable=False)
    id_cambio_original = db.Column(db.Integer, db.ForeignKey('CambioGuardia.id'), nullable=True)
    estado_confirmacion = db.Column(SqlEnum(EstadoConfirmacion), default=EstadoConfirmacion.pendiente, nullable=False)
    fecha_confirmacion = db.Column(db.DateTime, nullable=True)



class ParteNovedades(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    numero_legajo = db.Column(db.Integer, nullable=False)
    nombre_solicitante = db.Column(db.String(100), nullable=False)
    destino = db.Column(db.String(100), nullable=False)  # Para
    objeto = db.Column(db.String(200), nullable=False)
    detalle = db.Column(db.Text, nullable=False)
    archivo_pdf = db.Column(db.String(200), nullable=True)  # <- Nueva columna
    estado_confirmacion = db.Column(SqlEnum(EstadoConfirmacion), default=EstadoConfirmacion.pendiente, nullable=False)
    fecha_confirmacion = db.Column(db.DateTime, nullable=True)

class Notificacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mensaje = db.Column(db.String(255), nullable=False)
    leida = db.Column(db.Boolean, default=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación opcional para acceder desde el usuario
    usuario = db.relationship('User', backref='notificaciones')


class ResponsableArea(db.Model):
    __tablename__ = 'responsables_area'
    id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String(100), unique=True, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    usuario = db.relationship('User', backref='responsable_de_area')

# Line below only required once, when creating DB.
with app.app_context():
    db.create_all()



#------------------------------------------#------------------------------------------

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#------------------------------------------#----------------------------------------------

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
#------------------------------------------#------------------------------------------

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.rol not in roles:
                flash('No tenés permiso para acceder a esta página.')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

#----------------------------------------------#-----------PAGINA DE INICIO-----------------------------------
@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Usuario no encontrado")
            return redirect(url_for('index'))

        elif not check_password_hash(user.password, password):
            flash("Contraseña incorrecta")
            return redirect(url_for('index'))
        else:
            login_user(user)
            return redirect(url_for("acces"))
    return render_template("index.html")


@login_manager.unauthorized_handler
def unauthorized():
    # Esta función se llama cuando un usuario no logueado intenta acceder a una ruta protegida
    return render_template('acceso_denegado.html'), 403
#----------------------------------------------#---PAGINA DEL MENU-------------------------------------------
@app.route('/acces')
@login_required
def acces():
    # Obtén el número de legajo del usuario actual
    legajo_usuario = current_user.numero_legajo

    # Consulta en la tabla Bomberos para obtener el DNI usando el número de legajo
    bombero = Bomberos.query.filter_by(legajo_numero=legajo_usuario).first()
    if bombero is None:
        return "Bombero no encontrado", 404
    dni = bombero.dni
    horas_acumuladas = calcular_horas_y_minutos_acumulados(dni)
    return render_template("acces.html", name=current_user.name, horas_acumuladas=horas_acumuladas)

#----------------------------------------------#---------REGISTRAR UN NUEVO USUARIO-------------------------------------

@app.route('/register', methods=["GET", "POST"])
@login_required
def register():
    if request.method == "POST":
        hash_password = generate_password_hash(request.form.get("password"),
                                               method='pbkdf2:sha256',
                                               salt_length=6)
        new_user = User(
            email=request.form.get("email"),
            name=request.form.get("name"),
            numero_legajo=request.form.get("numero_legajo"),
            password=hash_password,
            telefono=request.form.get("telefono"),
            rol=request.form.get("role")  # Make sure your form includes a role field
        )
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("acces"))
    return render_template("register.html")


#----------------------------------------------

# Mostrar usuarios y roles
@app.route("/usuarios")
@login_required
@role_required('admin')
def usuarios():
    if not current_user.rol == 'admin':
        flash('Acceso no autorizado')
        return redirect(url_for('index'))
    usuarios = User.query.all()
    return render_template("gestionar_roles.html", usuarios=usuarios)


@app.route("/cambiar_rol/<int:user_id>", methods=["POST"])
@login_required
@role_required('admin')
def cambiar_rol(user_id):
    if not current_user.rol == 'admin':
        flash('Acceso no autorizado')
        return redirect(url_for('index'))

    user = User.query.get_or_404(user_id)
    nuevo_rol = request.form.get("nuevo_rol")

    if nuevo_rol not in ["usuario", "admin", "jefe_guardia"]:
        flash("Rol no válido.")
        return redirect(url_for('usuarios'))

    user.rol = nuevo_rol
    db.session.commit()
    flash(f"Rol de {user.name} actualizado a {nuevo_rol}.")
    return redirect(url_for('usuarios'))

#----------------------------------------------#-------PAGINA PARA CARGAR LOS DATOS---------------------------------------

@app.route('/cargadatos', methods=["GET", "POST"])
@login_required
@role_required('admin')
def cargadatos():
    if request.method == "POST":
        if 'registrar_bombero' in request.form:
            fecha_nac_str = request.form.get("fecha_nacimiento")
            try:
                fecha_nacimiento = datetime.strptime(fecha_nac_str, '%Y-%m-%d').date()
            except ValueError:
                flash("Error: Formato de fecha incorrecto. Asegúrate de que las fechas estén en el formato 'YYYY-MM-DD'")
                return redirect(url_for("cargadatos"))

            dni_pdf = request.files["dni_pdf"]
            ficha_path = None
            if dni_pdf and allowed_file(dni_pdf.filename):
                filename_pdf = secure_filename(dni_pdf.filename)
                file_path_pdf = os.path.join(app.config['UPLOAD_FOLDER'],"dni_pdf")

                # Asegura que el directorio exista sin lanzar un error si ya existe
                if not os.path.exists(file_path_pdf):
                    os.makedirs(filename_pdf)

                    # Guardar el archivo en la carpeta
                    ruta_archivo = os.path.join(file_path_pdf, dni_pdf)
                    dni_pdf.save(ruta_archivo)
                    ficha_path = os.path.join(dni_pdf)
            else:
                relative_file_path_pdf = None




            nuevo_bombero = Bomberos(
                legajo_numero=request.form.get("legajo_numero"),
                apellido=request.form.get("apellido"),
                nombre=request.form.get("nombre"),
                dni=request.form.get("dni"),
                dni_pdf=ficha_path,
                telefono=request.form.get("telefono"),
                telefono_alternativo=request.form.get("telefono_alternativo"),
                fecha_nacimiento=fecha_nacimiento,
                domicilio=request.form.get("domicilio"),
                email=request.form.get("email"),
                rol=request.form.get("rol"),
                grupo_sanguineo=request.form.get("grupo_sanguineo"),
                alergia=request.form.get("alergia"),
                camada=request.form.get("camada"),
                obra_scocial=request.form.get("social"),
                registro=current_user.name,
                nivel_educativo=request.form.get("nivel_educativo")
            )
            db.session.add(nuevo_bombero)
            db.session.commit()
            flash("Bombero registrado exitosamente")
            return redirect(url_for("acces"))



        if 'registrar_indumentaria' in request.form:
            nueva_indumentaria = IndumentariaProvista(
                numero_legajo=request.form.get("numero_legajo"),
                gorra=request.form.get("gorra"),
                remera_azul=request.form.get("remera_azul"),
                pantalon_fajina=request.form.get("pantalon_fajina"),
                borcegos=request.form.get("borcegos"),
                rompeviento=request.form.get("rompe_viento"),
                camp_neopren=request.form.get("camp_neopren"),
                bermuda=request.form.get("bermuda")
            )
            db.session.add(nueva_indumentaria)
            db.session.commit()
            flash("Indumentaria registrada exitosamente")
            return redirect(url_for("acces"))

        if 'registrar_licencia' in request.form:
            fecha_otorgacion_str = request.form.get("fecha_otorgacion")
            fecha_vencimiento_str = request.form.get("fecha_vencimiento")
            try:
                fecha_otorgacion = datetime.strptime(fecha_otorgacion_str, '%Y-%m-%d').date()
                fecha_vencimiento = datetime.strptime(fecha_vencimiento_str, '%Y-%m-%d').date()
            except ValueError:
                flash(
                    "Error: Formato de fecha incorrecto. Asegúrate de que las fechas estén en el formato 'YYYY-MM-DD'")
                return redirect(url_for("cargadatos"))

            file_frente = request.files['lic_frente']
            file_dorso = request.files['lic_dorso']
            if file_frente and allowed_file(file_frente.filename):
                filename_frente = secure_filename(file_frente.filename)
                file_path_frente = os.path.join(app.config['UPLOAD_FOLDER'], 'licencias', filename_frente)
                os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'licencias'), exist_ok=True)
                file_frente.save(file_path_frente)
                relative_file_path_frente = os.path.join(filename_frente)
            else:
                relative_file_path_frente = None

            if file_dorso and allowed_file(file_dorso.filename):
                filename_dorso = secure_filename(file_dorso.filename)
                file_path_dorso = os.path.join(app.config['UPLOAD_FOLDER'], 'licencias', filename_dorso)
                os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'licencias'), exist_ok=True)
                file_dorso.save(file_path_dorso)
                relative_file_path_dorso = os.path.join('uploads', 'licencias', filename_dorso)
            else:
                relative_file_path_dorso = None

            nueva_licencia = Licencias_Conducir(
                numero_legajo=request.form.get("numero_legajo"),
                tipo=request.form.get("tipo"),
                fecha_otorgacion=fecha_otorgacion,
                fecha_vencimiento=fecha_vencimiento,
                observacion=request.form.get("observacion"),
                lic_frente=relative_file_path_frente,
                lic_dorso=relative_file_path_dorso
            )
            db.session.add(nueva_licencia)
            db.session.commit()
            flash("Licencia de conducir registrada exitosamente")
            return redirect(url_for("acces"))

        if 'registrar_epp' in request.form:
            print("Registrar EPP")
            nuevo_epp = Epp_provisto(
                numero_legajo=request.form.get("numero_legajo"),
                casco_estructural=request.form.get("casco_estructural"),
                monja_estructural=request.form.get("monja_estructural"),
                guantes__estructural=request.form.get("guantes_estructural"),
                chaqueton_estructural=request.form.get("chaqueton_estructural"),
                pantalon_estructural=request.form.get("pantalon_estructural"),
                botas_estructural=request.form.get("botas_estructural"),
                monja_forestal=request.form.get("monja_forestal"),
                camisa_forestal=request.form.get("camisa_forestal"),
                guantes_forestal=request.form.get("guantes_forestal"),
                pantalon_forestal=request.form.get("pantalon_forestal"),
                antiparras_forestal=request.form.get("antiparras_forestal"),
                linterna_forestal=request.form.get("linterna_forestal")
            )
            db.session.add(nuevo_epp)
            db.session.commit()
            flash("Epp registrado exitosamente")
            return redirect(url_for("acces"))

    return render_template("cargadatos.html")
#----------------------------------------------#-------PAGINA DE LEGAJOS---------------------------------------
@app.route('/legajosvcp')
@login_required
def legajosvcp():
    if current_user.rol == 'admin':
        bomberos = Bomberos.query.order_by(Bomberos.legajo_numero).all()
        licencias = Licencias_Conducir.query.order_by(Licencias_Conducir.numero_legajo).all()
    else:
        # Filtra para mostrar solo el legajo del usuario
        bomberos = Bomberos.query.filter_by(legajo_numero=current_user.numero_legajo).all()
        licencias = Licencias_Conducir.query.filter_by(numero_legajo=current_user.numero_legajo).all()

    return render_template("legajosvcp.html", bomberos=bomberos, licencias=licencias)


#------------------------------------------#------EDICION DE LOS LEGAJOS----------------------------------------
@app.route('/legajosvcp/edit/<int:id>', methods=["GET", "POST"])
@login_required
def edit_legajo(id):
    legajo = Bomberos.query.get_or_404(id)
    if request.method == "POST":
        legajo.legajo_numero = request.form.get("legajo_numero")
        legajo.apellido = request.form.get("apellido")
        legajo.nombre = request.form.get("nombre")
        legajo.dni = request.form.get("dni")
        legajo.telefono = request.form.get("telefono")
        legajo.telefono_alternativo = request.form.get("telefono_alternativo")

        fecha_nacimiento_str = request.form.get("fecha_nacimiento")
        if fecha_nacimiento_str:
            legajo.fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, '%Y-%m-%d').date()

        legajo.domicilio = request.form.get("domicilio")
        legajo.email = request.form.get("email")
        legajo.rol = request.form.get("rol")
        legajo.grupo_sanguineo = request.form.get("grupo_sanguineo")
        legajo.alergia = request.form.get("alergia")
        legajo.camada = request.form.get("camada")
        legajo.estado = request.form.get("estado")
        legajo.obra_scocial = request.form.get("obra_social")
        legajo.registro = request.form.get("registro")
        legajo.nivel_educativo = request.form.get("nivel_educativo")

        # Manejo del archivo dni_pdf
        if 'dni_pdf' in request.files:
            file = request.files['dni_pdf']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], "dni_pdf", filename))
                legajo.dni_pdf = filename

        # Guarda los cambios en la base de datos
        try:
            db.session.commit()
            flash("Legajo actualizado correctamente.")
        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar el legajo: {str(e)}")
            return redirect(url_for('edit_legajo', id=id))

        return redirect(url_for('acces'))

    return render_template('edit_legajo.html', legajo=legajo)




#----------------------------------------------#--------------ELIMINAR BOMBERO--------------------------------

@app.route('/eliminar_bombero/<int:legajo>', methods=['POST'])
@role_required('admin')
@login_required
def eliminar_bombero(legajo):
    bombero = Bomberos.query.get_or_404(legajo)
    db.session.delete(bombero)
    db.session.commit()
    return jsonify({'success': True})

#----------------------------------------------#-----LICENCIAS DE CONDUCIR-----------------------------------------
@app.route('/licencias_conducir')
@login_required
def licencias_conducir():
    if current_user.rol == 'admin':
        bomberos = Bomberos.query.order_by(Bomberos.legajo_numero).all()
        licencias = Licencias_Conducir.query.order_by(Licencias_Conducir.numero_legajo).all()
    else:
        # Filtra para mostrar solo el legajo del usuario
        bomberos = Bomberos.query.filter_by(legajo_numero=current_user.numero_legajo).all()
        licencias = Licencias_Conducir.query.filter_by(numero_legajo=current_user.numero_legajo).all()

    return render_template("licencias_conducir.html", bomberos=bomberos, licencias=licencias)

#----------------------------------------------#-----EDITAR LICENCIAS DE CONDUCIR-----------------------------------------
@app.route('/legajosvcp/edit_licencia/<int:id>', methods=["GET", "POST"])
@login_required
def edit_licencia(id):
    licencia = Licencias_Conducir.query.get_or_404(id)
    if request.method == "POST":
        licencia.tipo = request.form.get("tipo")

        fecha_otorgacion_str = request.form.get("fecha_otorgacion")
        fecha_vencimiento_str = request.form.get("fecha_vencimiento")

        if fecha_otorgacion_str:
            licencia.fecha_otorgacion = datetime.strptime(fecha_otorgacion_str, '%Y-%m-%d').date()
        if fecha_vencimiento_str:
            licencia.fecha_vencimiento = datetime.strptime(fecha_vencimiento_str, '%Y-%m-%d').date()

        licencia.observacion = request.form.get("observacion")

        if 'lic_frente' in request.files:
            file = request.files['lic_frente']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'],'licencias',  filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(file_path)
                licencia.lic_frente = os.path.join('uploads','licencias', filename)

        if 'lic_dorso' in request.files:
            file = request.files['lic_dorso']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'],'licencias', filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(file_path)
                licencia.lic_dorso = os.path.join('uploads','licencias', filename)

        db.session.commit()
        flash("Licencia actualizada exitosamente")
        return redirect(url_for('licencias_conducir'))

    return render_template('edit_licencia.html', licencia=licencia)

#----------------------------------------------#--------------ELIMINAR BOMBERO--------------------------------

@app.route('/eliminar_licencia/<int:legajo>', methods=['POST'])
@role_required('admin')
@login_required
def eliminar_licencia(id):
    licencia = Licencias_Conducir.query.get_or_404(id)
    db.session.delete(licencia)
    db.session.commit()
    return jsonify({'success': True})


#-------------------------------------------------CAMBIOS DE GUARDIA NUEVOS 2025-------------------------------

@app.route('/cambio_guardia', methods=['GET', 'POST'])
@login_required
def cambio_guardia():
    if request.method == 'POST':
        tz_buenos_aires = pytz.timezone('America/Argentina/Buenos_Aires')

        fecha_actual = datetime.now(tz_buenos_aires).date()

        # Obtener la hora actual en Buenos Aires
        hora_actual_utc = datetime.now(timezone('UTC'))
        hora_actual_buenos_aires = hora_actual_utc.astimezone(app.config['TIMEZONE'])

        # Convertir la hora a un objeto 'time' de Python
        hora_actual_str = hora_actual_buenos_aires.strftime('%H:%M')
        hora_actual_obj = datetime.strptime(hora_actual_str, '%H:%M').time()

        tipo_solicitud = request.form.get('tipo_solicitud')
        if not tipo_solicitud:
            flash("Debe seleccionar un tipo de solicitud", "danger")
            return redirect(url_for('cambio_guardia'))
        #legajo_solicitante = int(request.form['legajo_solicitante'])
        motivo = request.form['motivo']
        fecha_ausencia = datetime.strptime(request.form['fecha_ausencia'], '%Y-%m-%d').date()
        jefe_guardia = request.form['jefe_guardia']
        hora_desde = datetime.strptime(request.form['hora_desde'], '%H:%M').time()
        hora_hasta = datetime.strptime(request.form['hora_hasta'], '%H:%M').time()
        legajo_quien_cubre = int(request.form['legajo_quien_cubre'])

        id_cambio_original = request.form.get('id_cambio_original')
        id_cambio_original = int(id_cambio_original) if id_cambio_original else None

        nuevo_cambio = CambioGuardia(
            fecha=fecha_actual,
            hora=hora_actual_obj,
            tipo_solicitud=tipo_solicitud,
            legajo_solicitante=current_user.numero_legajo,
            motivo=motivo,
            fecha_ausencia=fecha_ausencia,
            jefe_guardia=jefe_guardia,
            hora_desde=hora_desde,
            hora_hasta=hora_hasta,
            legajo_quien_cubre=legajo_quien_cubre,
            id_cambio_original=id_cambio_original,
            estado_confirmacion=EstadoConfirmacion.pendiente
        )

        db.session.add(nuevo_cambio)
        db.session.commit()
        flash('Cambio registrado correctamente.'
              'Pendiente de confirmacion')

        # Buscar el usuario que debe cubrir la guardia
        usuario_cubre = User.query.filter_by(numero_legajo=legajo_quien_cubre).first()

        if usuario_cubre:
            mensaje = f"Tienes un nuevo cambio de guardia para cubrir el día {fecha_ausencia.strftime('%d/%m/%Y')} desde {hora_desde.strftime('%H:%M')} hasta {hora_hasta.strftime('%H:%M')}."
            nueva_notificacion = Notificacion(
                usuario_id=usuario_cubre.id,
                mensaje=mensaje
            )
            db.session.add(nueva_notificacion)
            db.session.commit()

        return redirect(url_for('cambio_guardia'))

    usuarios = {u.numero_legajo: u.name for u in User.query.all()}
    cambios = CambioGuardia.query.order_by(CambioGuardia.id.desc()).all()
    return render_template('cambio_guardia.html', cambios=cambios, usuarios=usuarios)
#------------------------------------------CONFIRMAR CAMBIO DE GUARDIA------------------------------
@app.route('/confirmar_cobertura/<int:id_cambio>', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'jefe_guardia')
def confirmar_cobertura(id_cambio):
    cambio = CambioGuardia.query.get_or_404(id_cambio)

    if request.method == 'POST':
        decision = request.form.get('decision')
        if decision == 'confirmar':
            cambio.estado_confirmacion = EstadoConfirmacion.confirmado
            cambio.fecha_confirmacion = datetime.now()
            flash('Has confirmado la cobertura.', 'success')
        elif decision == 'rechazar':
            cambio.estado_confirmacion = EstadoConfirmacion.rechazado
            cambio.fecha_confirmacion = datetime.now()
            flash('Has rechazado la cobertura.', 'warning')

        db.session.commit()
        return redirect(url_for('cambio_guardia'))  # O donde quieras redirigir

    return render_template('confirmar_cobertura.html', cambio=cambio)
#-----------------------------------ELIMINAR CAMBIO DE GUARDIA----------------------------
@app.route('/eliminar-cambio-guardia/<int:id>', methods=['POST'])
@login_required
def eliminar_cambio_guardia(id):
    # Buscar el cambio de guardia
    cambio = CambioGuardia.query.get_or_404(id)

    # Seguridad: Solo un admin o jefe de guardia puede eliminar
    if current_user.rol not in ['admin', 'jefe_guardia']:
        flash('No tienes permiso para eliminar este cambio de guardia.')
        return redirect(url_for('cambio_guardia'))

    try:
        db.session.delete(cambio)
        db.session.commit()
        flash('Cambio de guardia eliminado exitosamente.')
    except Exception as e:
        db.session.rollback()
        flash(f'Error eliminando el cambio de guardia: {str(e)}')

    return redirect(url_for('cambio_guardia'))

#----------------------------------------------#--------------CAMBIOS DE GUARDIA--------------------------------
#@app.route('/cambiosguardia', methods=['GET', 'POST'])
#@login_required
#def cambiosguardia():
#    if request.method == 'POST':
#        if 'registrar_cambio_guardia' in request.form:
#            numero_legajo = current_user.numero_legajo
#            fecha_solicitud = request.form.get("fecha_solicitud")
#            rango_horario = request.form.get("rango_horario")
#            rango_horario2 = request.form.get("rango_horario2")
#            legajo_quien_cubre = request.form.get("legajo_quien_cubre")
#            motivo = request.form.get("motivo")
#            fecha_devolucion = request.form.get("fecha_devolucion")
#            imagen = request.files.get("imagen")
#            imagen_filename = None
#
#            if imagen and allowed_file(imagen.filename):
#                filename = secure_filename(imagen.filename)
#                imagen_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'licencias', filename)
#                os.makedirs(os.path.dirname(imagen_filename), exist_ok=True)
#                imagen.save(imagen_filename)
#                imagen_filename = os.path.join('uploads', 'licencias', filename)  # Guardar la ruta relativa
#
#
#            nuevo_cambio = Cambios_Guardia(
#                numero_legajo=numero_legajo,
#                fecha_solicitud=datetime.strptime(fecha_solicitud, '%Y-%m-%d').date(),
#                rango_horario=datetime.strptime(rango_horario, '%H:%M').time(),
#                rango_horario2=datetime.strptime(rango_horario2, '%H:%M').time(),
#                legajo_quien_cubre=legajo_quien_cubre,
#                motivo=motivo,
#                fecha_devolucion=datetime.strptime(fecha_devolucion, '%Y-%m-%d').date(),
#                imagen=imagen_filename
#
#            )
#            db.session.add(nuevo_cambio)
#            db.session.commit()
#            flash("Cambio de guardia registrado exitosamente")
#            return redirect(url_for("cambiosguardia"))
#
#
#
#    cambios = Cambios_Guardia.query.all()
#    apellidos = {bombero.legajo_numero: bombero.apellido for bombero in Bomberos.query.all()}
#    return render_template("cambiosguardia.html", cambios=cambios, apellidos=apellidos)
#----------------------------------------------#-----------EDITAR CAMBIOS DE GUARDIA-----------------------------------
#@app.route('/editar_cambio_guardia/<int:id>', methods=["GET", "POST"])
#@login_required
#@role_required('admin')
#def editar_cambio_guardia(id):
#    cambio_guardia = Cambios_Guardia.query.get_or_404(id)
#
#    if request.method == "POST":
#
#        cambio_guardia.legajo_quien_cubre = request.form.get("legajo_quien_cubre")
#        cambio_guardia.motivo = request.form.get("motivo")
#        cambio_guardia.fecha_devolucion = datetime.strptime(request.form.get("fecha_devolucion"), '%Y-%m-%d').date()
#        cambio_guardia.aprovado = request.form.get("aprovado")
#
#        db.session.commit()
#        flash("Solicitud de cambio de guardia actualizada exitosamente")
#        return redirect(url_for("cambiosguardia"))
#
#    return render_template("editar_cambio_guardia.html", cambio_guardia=cambio_guardia)
#
#
#----------------------------------------------#---------ELIMINAR CAMBIO GUARDIA-------------------------------------
#@app.route('/eliminar_cambio_guardia/<int:id>', methods=['POST'])
#@role_required('admin')
#@login_required
#def eliminar_cambio_guardia(id):
#    try:
#        cambiog = Cambios_Guardia.query.get_or_404(id)
#        db.session.delete(cambiog)
#        db.session.commit()
#        return jsonify({"success": True, "message": "Registro de cambio de guardia eliminado exitosamente."})
#    except Exception as e:
#        db.session.rollback()
#        return jsonify({"success": False, "message": "Hubo un problema al eliminar el registro."}), 500
#

#----------------------------------------------#---------MATERIALES Y EQUIPO-------------------------------------


@app.route('/matyequipo', methods=["GET", "POST"])
@login_required
def matyequipo():
    indumentaria= IndumentariaProvista.query.order_by(IndumentariaProvista.numero_legajo).all()
    bomber = Bomberos.query.order_by(Bomberos.legajo_numero).all()
    provisto=Epp_provisto.query.order_by(Epp_provisto.numero_legajo).all()

    return render_template("matyequipo.html", indu=indumentaria, bomberos=bomber, provisto=provisto)


#----------------------------------------------#---EDITAR  EPP------------------------------------------

@app.route('/matyequipo/edit/<int:id>', methods=["GET", "POST"])
@role_required('admin')
@login_required
def edit_matyequipo(id):
    # Obtener instancias de ambos modelos
    provisto = Epp_provisto.query.get_or_404(id)
    indumentaria = IndumentariaProvista.query.get_or_404(id)

    # Procesar el formulario de 'EPP Provisto'
    if request.method == "POST" and 'submit_provisto' in request.form:
        provisto.casco_estructural = request.form.get("casco_estructural")
        provisto.monja_estructural = request.form.get("monja_estructural")
        provisto.guantes_estructural = request.form.get("guantes_estructural")
        provisto.chaqueton_estructural = request.form.get("chaqueton_estructural")
        provisto.pantalon_estructural = request.form.get("pantalon_estructural")
        provisto.botas_estructural = request.form.get("botas_estructural")
        provisto.monja_forestal = request.form.get("monja_forestal")
        provisto.camisa_forestal = request.form.get("camisa_forestal")
        provisto.guantes_forestal = request.form.get("guantes_forestal")
        provisto.pantalon_forestal = request.form.get("pantalon_forestal")
        provisto.antiparras_forestal = request.form.get("antiparras_forestal")
        provisto.linterna_forestal = request.form.get("linterna_forestal")

        db.session.commit()
        flash("Registro de EPP actualizado exitosamente")
        return redirect(url_for('matyequipo'))

    # Procesar el formulario de 'Indumentaria Provista'
    if request.method == "POST" and 'submit_indumentaria' in request.form:
        indumentaria.gorra = request.form.get("gorra")
        indumentaria.remera_azul = request.form.get("remera_azul")
        indumentaria.pantalon_fajina = request.form.get("pantalon_fajina")
        indumentaria.borcegos = request.form.get("borcegos")
        indumentaria.rompeviento = request.form.get("rompeviento")
        indumentaria.camp_neopren = request.form.get("camp_neopren")
        indumentaria.bermuda = request.form.get("bermuda")

        db.session.commit()
        flash("Registro de indumentaria actualizado exitosamente")
        return redirect(url_for('matyequipo'))

    return render_template('edit_matyequipo.html', provisto=provisto, indumentaria=indumentaria)



#--------------------------------------PARTES DE LICENCIA--------#----------------------------------------------
@app.route('/partes', methods=['GET', 'POST'])
@login_required
def partes_licencia():
    if request.method == "POST":
        if 'registrar_parte' in request.form:
            archivo_parte = request.files['parte_licencia']

            if archivo_parte and allowed_file(archivo_parte.filename):
                filename_parte = secure_filename(archivo_parte.filename)
                archivo_parte.save(os.path.join(app.config['UPLOAD_FOLDER'],"partes", filename_parte))
                #   parte_path = os.path.join(app.config['UPLOAD_FOLDER'],"licencias", filename_parte)


                try:
                    fecha_inicio_licencia = datetime.strptime(request.form.get("fecha_inicio_licencia"), '%Y-%m-%d').date()
                    fecha_fin_licencia = datetime.strptime(request.form.get("fecha_fin_licencia"), '%Y-%m-%d').date()
                except ValueError:
                    flash("Error: Formato de fecha incorrecto.")
                    return redirect(url_for("partes_licencia"))
                fecha_actual = datetime.now().date()
                nuevo_parte = Partes_Licencia(
                    numero_legajo=current_user.numero_legajo,
                    tipo_licencia=request.form.get("tipo_licencia"),
                    fecha_solicitud=fecha_actual,
                    fecha_inicio_licencia=fecha_inicio_licencia,
                    fecha_fin_licencia=fecha_fin_licencia,
                    parte_licencia=filename_parte
                )
                db.session.add(nuevo_parte)
                db.session.commit()
                flash("Parte de licencia registrado exitosamente")
                return redirect(url_for("acces"))
            else:
                print("error")
                flash("Error: Formato de archivo no permitido.")
                return redirect(url_for("partes_licencia"))
    solicitudes = Partes_Licencia.query.all()
    return render_template("partes.html", solicitudes=solicitudes)

#----------------------------------------------Partes 2025----------------------------

@app.route('/parte_novedades', methods=['GET', 'POST'])
@login_required
def parte_novedades():
    if request.method == 'POST':
        try:
            destino = request.form['area_destino']
            objeto = request.form['objeto']
            detalle = request.form['detalle']

            # Datos automáticos
            fecha_actual = datetime.now().date()
            hora_actual = datetime.now().time()
            legajo = current_user.numero_legajo
            nombre = current_user.name

            # Crear registro en la BD
            nuevo_parte = ParteNovedades(
                fecha=fecha_actual,
                hora=hora_actual,
                numero_legajo=legajo,
                nombre_solicitante=nombre,
                destino=destino,
                objeto=objeto,
                detalle=detalle,
                estado_confirmacion=EstadoConfirmacion.pendiente
            )
            db.session.add(nuevo_parte)
            db.session.commit()  # Aquí se genera el ID

            # 🔔 Enviar notificación al responsable de área
            responsable = ResponsableArea.query.filter_by(area=destino).first()
            if responsable:
                notificacion = Notificacion(
                    usuario_id=responsable.usuario_id,
                    mensaje=f"Nuevo parte generado por {nombre} para el área {destino}.",
                    leida=False
                )
                db.session.add(notificacion)
                db.session.commit()

            # Crear PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            # Insertar logo (asegurate que exista)
            logo_path = os.path.join(app.root_path, 'static', 'img', 'logo1.png')
            if os.path.exists(logo_path):
                pdf.image(logo_path, x=160, y=10, w=40)

            pdf.set_xy(10, 20)
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "PARTE DE NOVEDADES", ln=True, align="C")
            pdf.ln(10)

            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, f"De: {nombre} (Legajo {legajo})\nPara: {destino}\nFecha: {fecha_actual.strftime('%d/%m/%Y')} - Hora: {hora_actual.strftime('%H:%M')}")
            pdf.ln(5)
            pdf.cell(0, 10, f"Objeto: {objeto}", ln=True)
            pdf.ln(5)
            pdf.multi_cell(0, 10, f"DETALLE:\n{detalle}")
            pdf.ln(50)
            pdf.cell(0, 10, "Recibido: ___________________", ln=True)
            pdf.cell(0, 10, "Autorizado: __________________", ln=True)

            # Guardar PDF
            ruta_carpeta = os.path.join(app.root_path, 'static', 'partes_generados')

            os.makedirs(ruta_carpeta, exist_ok=True)

            nombre_archivo_pdf = f"parte_{nuevo_parte.id}.pdf"
            ruta_pdf = os.path.join(ruta_carpeta, nombre_archivo_pdf)

            pdf.output(ruta_pdf)

            # Actualizar registro con el nombre del PDF
            nuevo_parte.archivo_pdf = nombre_archivo_pdf
            db.session.commit()

            flash("Parte generado y guardado correctamente.", "success")
            return redirect(url_for('parte_novedades'))

        except Exception as e:
            flash(f"Error al generar el parte: {str(e)}", "danger")
            return redirect(url_for('parte_novedades'))

    # Mostrar historial
    if current_user.rol in ['admin', 'jefe_guardia']:
        partes = ParteNovedades.query.order_by(ParteNovedades.id.desc()).all()
    else:
            partes = ParteNovedades.query.filter_by(numero_legajo=current_user.numero_legajo).order_by(ParteNovedades.id.desc()).all()
    return render_template("parte_novedades.html", partes=partes)

#------------------------------------PARTE APROBACION-------------------------------------------------------
@app.route('/parte_aprobado/<int:id_cambio>', methods=['GET', 'POST'])
@login_required
@role_required('admin','jefe_guardia')
def parte_aprobado(id_cambio):
    parte = ParteNovedades.query.get_or_404(id_cambio)

    if request.method == 'POST':
        decision = request.form.get('decision')
        if decision == 'confirmar':
            parte.estado_confirmacion = EstadoConfirmacion.confirmado
            parte.fecha_confirmacion = datetime.now()
            flash('Has confirmado la cobertura.', 'success')
        elif decision == 'rechazar':
            parte.estado_confirmacion = EstadoConfirmacion.rechazado
            parte.fecha_confirmacion = datetime.now()
            flash('Has rechazado la cobertura.', 'warning')

        db.session.commit()
        return redirect(url_for('parte_novedades'))  # O donde quieras redirigir

    return render_template('parte_aprobado.html', parte=parte)
#----------------------------------------------#----------------------------------------------
@app.route('/eliminar_parte/<int:id>', methods=['POST'])
@login_required
def eliminar_parte(id):
    if current_user.rol not in ['admin', 'jefe_guardia']:
        flash("No tenés permiso para eliminar partes.", "danger")
        return redirect(url_for('parte_novedades'))

    parte = ParteNovedades.query.get_or_404(id)

    # Eliminar PDF si existe
    if parte.archivo_pdf:
        ruta_pdf = os.path.join(app.root_path, 'static', 'partes_generados', parte.archivo_pdf)
        if os.path.exists(ruta_pdf):
            os.remove(ruta_pdf)

    db.session.delete(parte)
    db.session.commit()
    flash("Parte eliminado correctamente.", "success")
    return redirect(url_for('parte_novedades'))


#----------------------------------------------#----------------------------------------------
@app.route('/uploads/partes/<filename>')
def download_file(filename):
    subdirectory = "partes"
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], subdirectory), filename)

@app.route('/uploads/parte_novedades/<filename>')
def download_fil(filename):
    subdirectory = "parte"
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], subdirectory), filename)

@app.route('/uploads/ficha_medica/<filename>')
def download_files(filename):
    subdirectory = "ficha_medica"
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], subdirectory), filename)


@app.route('/uploads/dni_pdf/<filename>')
def download_filesss(filename):
    subdirectory = "dni_pdf"
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], subdirectory), filename)

@app.route('/uploads/licencias/<filename>')
def download_filess(filename):
    subdirectory = "licencias"
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], subdirectory), filename)
#----------------------------------------FICHA MEDICA------#----------------------------------------------

@app.route('/fichas_medicas', methods=['GET', 'POST'])
@login_required
def fichas_medicas():
    if request.method == "POST":
        if 'registrar_ficha' in request.form:
            archivo_ficha = request.files['pdf_ficha_medica']

            if archivo_ficha and allowed_file(archivo_ficha.filename):
                filename_ficha = secure_filename(archivo_ficha.filename)
                ruta_directorio = os.path.join(app.config['UPLOAD_FOLDER'], 'ficha_medica')

                # Verificar si la carpeta 'ficha_medica' existe, y si no, crearla
                if not os.path.exists(ruta_directorio):
                    os.makedirs(ruta_directorio)

                # Guardar el archivo en la carpeta
                ruta_archivo = os.path.join(ruta_directorio, filename_ficha)
                archivo_ficha.save(ruta_archivo)
                ficha_path = os.path.join(filename_ficha)

                try:
                    fecha_ficha = datetime.strptime(request.form.get("fecha_ficha"), '%Y-%m-%d').date()
                except ValueError:
                    flash("Error: Formato de fecha incorrecto.")
                    return redirect(url_for("fichas_medicas"))

                nueva_ficha = Ficha_Medica(
                    numero_legajo=request.form.get("numero_legajo"),
                    fecha_ficha=fecha_ficha,
                    observaciones=request.form.get("observaciones"),
                    pdf_ficha_medica=ficha_path
                )
                db.session.add(nueva_ficha)
                db.session.commit()
                flash("Ficha médica registrada exitosamente")
                return redirect(url_for("fichas_medicas"))
            else:
                flash("Error: Formato de archivo no permitido.")
                return redirect(url_for("fichas_medicas"))

    if current_user.rol == 'admin':
        bomberos = Bomberos.query.order_by(Bomberos.legajo_numero).all()
        fichas = Ficha_Medica.query.order_by(Ficha_Medica.numero_legajo).all()
    else:
        # Filtra para mostrar solo el legajo del usuario
        bomberos = Bomberos.query.filter_by(legajo_numero=current_user.numero_legajo).all()
        fichas = Ficha_Medica.query.filter_by(numero_legajo=current_user.numero_legajo).all()

    return render_template("fichas_medicas.html", fichas=fichas, bomberos=bomberos)


#----------------------------------------ELIMINAR FICHA MEDICA------#----------------------------------------------


@app.route('/eliminar_ficha_medica/<int:id>', methods=['POST'])
@role_required('admin')
@login_required
def eliminar_ficha_medica(id):
    try:
        ficha = Ficha_Medica.query.get_or_404(id)
        db.session.delete(ficha)
        db.session.commit()
        return jsonify({"success": True, "message": "Ficha médica eliminada exitosamente."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Hubo un problema al eliminar la ficha médica."}), 500


#---------------------------------------- EDITAR FICHA MEDICA------#----------------------------------------------

@app.route('/editar_ficha_medica/<int:id>', methods=['GET'])
@role_required('admin')
@login_required
def editar_ficha_medica(id):
    ficha = Ficha_Medica.query.get_or_404(id)
    return render_template('editar_ficha_medica.html', ficha=ficha)


@app.route('/actualizar_ficha_medica/<int:id>', methods=['POST'])
@role_required('admin')
@login_required
def actualizar_ficha_medica(id):
    ficha = Ficha_Medica.query.get_or_404(id)
    ficha.numero_legajo = request.form['numero_legajo']
    ficha.fecha_ficha = date.fromisoformat(request.form['fecha_ficha'])
    ficha.observaciones = request.form['observaciones']

    if 'pdf_ficha_medica' in request.files:
        file = request.files['pdf_ficha_medica']
        if file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            ficha.pdf_ficha_medica = filename

    db.session.commit()
    flash("Ficha médica actualizada exitosamente.")
    return redirect(url_for('fichas_medicas'))




#----------------------------------------TALLES------#----------------------------------------------

@app.route('/talles', methods=['GET', 'POST'])
@login_required
def talles():
    if request.method == "POST":
        numero_legajo = request.form.get("numero_legajo")
        remera_fajina = request.form.get("remera_fajina")
        pantalon_fajina = request.form.get("pantalon_fajina")
        campera_fajina = request.form.get("campera_fajina")
        borcegos = request.form.get("borcegos")

        # Validaciones
        if not numero_legajo or not remera_fajina or not pantalon_fajina or not campera_fajina or not borcegos:
            flash("Todos los campos son obligatorios.")
            return redirect(url_for("talles"))

        try:
            numero_legajo = int(numero_legajo)
            pantalon_fajina = int(pantalon_fajina)
            borcegos = int(borcegos)
        except ValueError:
            flash("Número de legajo, pantalón y borcegos deben ser números enteros.")
            return redirect(url_for("talles"))

        nuevo_talle = Talles(
            numero_legajo=numero_legajo,
            remera_fajina=remera_fajina,
            pantalon_fajina=pantalon_fajina,
            campera_fajina=campera_fajina,
            borcegos=borcegos
        )
        db.session.add(nuevo_talle)
        db.session.commit()
        flash("Talle registrado exitosamente")
        return redirect(url_for("talles"))

    bomberos = Bomberos.query.all()
    talles = Talles.query.all()
    return render_template("tallesbv.html", bomberos=bomberos, talles=talles)


#----------------------------------------------CONTACTOS#----------------------------------------------
@app.route('/contactos')
@login_required
def contactos():
    return render_template('contactos.html')


#----------------------------------------------modificar password#----------------------------------------------
@app.route('/update-password', methods=['POST'])
def update_password():
    email = request.form['email']
    current_password = request.form['current_password']
    new_password = request.form['new_password']

    # Buscar usuario por email
    user = User.query.filter_by(email=email).first()
    if user is None:
        flash("usuario no registrado")
        return redirect(url_for('register'))

    # Verificar la contraseña actual
    if not check_password_hash(user.password, current_password):
        flash("contraseña incorrecta")
        return redirect(url_for('register'))

    # Generar el nuevo hash para la nueva contraseña
    new_hashed_password = generate_password_hash(new_password)

    # Actualizar la contraseña en la base de datos
    user.password = new_hashed_password
    flash("Contraseña modificada con exito!!")
    db.session.commit()

    return render_template('acces.html')
#---------------------------------------------- Funcion de calcular horas Asistencia#----------------------------------------------
INSTITUTION_IP = ["190.195.11.53","186.108.89.24", "200.105.104.74", "170.51.250.38", "172.28.32.201", "104.28.63.27", "104.28.59.28"]
NOSTROSIP = ["cuarte etac casaale juli1 juli2 kossoyiphone kossoyiphone2"]

def calcular_horas_y_minutos_acumulados(dni):
    mes_actual = datetime.now().month
    año_actual = datetime.now().year

    inicio_mes = datetime(año_actual, mes_actual, 1)
    if mes_actual == 12:
        fin_mes = datetime(año_actual + 1, 1, 1) - timedelta(seconds=1)
    else:
        fin_mes = datetime(año_actual, mes_actual + 1, 1) - timedelta(seconds=1)

    asistencias_mes = Aistencia.query.filter(
        Aistencia.dni == dni,
        Aistencia.fecha.between(inicio_mes.date(), fin_mes.date())
    ).order_by(Aistencia.fecha, Aistencia.hora).all()

    horas_acumuladas = timedelta()
    entrada_actual = None

    for asistencia in asistencias_mes:
        if asistencia.tipo_registro == "INGRESO":
            if entrada_actual is None:
                entrada_actual = asistencia
        elif asistencia.tipo_registro == "SALIDA":
            if entrada_actual:
                try:
                    hora_entrada = datetime.strptime(entrada_actual.hora, '%H:%M').time()
                    hora_salida = datetime.strptime(asistencia.hora, '%H:%M').time()
                    tiempo_entrada = datetime.combine(entrada_actual.fecha, hora_entrada)
                    tiempo_salida = datetime.combine(asistencia.fecha, hora_salida)

                    if tiempo_salida > tiempo_entrada:
                        horas_acumuladas += tiempo_salida - tiempo_entrada
                except Exception as e:
                    print(f"Error: {e}")
                entrada_actual = None

    total_horas = int(horas_acumuladas.total_seconds() // 3600)
    total_minutos = int((horas_acumuladas.total_seconds() % 3600) // 60)
    return f"{total_horas} horas y {total_minutos} minutos"

#----------------------------------------------ASISTENCIAS ojo mal escrito------------------------------------------
@app.route('/asistencia', methods=['GET', 'POST'])
def asistencia():
    tz_buenos_aires = pytz.timezone('America/Argentina/Buenos_Aires')

    fecha_actual = datetime.now(tz_buenos_aires).date()
    hora_actual_utc = datetime.now(timezone('UTC'))
    hora_actual_buenos_aires = hora_actual_utc.astimezone(app.config['TIMEZONE'])
    hora_actual_str = hora_actual_buenos_aires.strftime('%H:%M')
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    print(client_ip)
    print("Esta es la IP")
    if not (current_user.is_authenticated and (current_user.rol == "admin" or current_user.rol == "jefe_guardia")):
        if client_ip not in INSTITUTION_IP:
            return redirect(url_for("error_red"))  # Redirige si la IP no es válida
        print(client_ip)

    if request.method == 'POST':
        dni = request.form.get('dni')
        agente_existente = Bomberos.query.filter_by(dni=dni).first()

        if not agente_existente:
            flash('No se puede registrar la asistencia. El DNI no está registrado.')
            return redirect(url_for("acces"))

        if not current_user.is_authenticated:
            # Obtener el último registro de asistencia del usuario
            ultimo_registro = Aistencia.query.filter_by(dni=dni).order_by(
                Aistencia.id_asistencia.desc()).first()

            # Verificar si el último registro fue "INGRESO" y la nueva solicitud es también "INGRESO"
            if ultimo_registro and ultimo_registro.tipo_registro == "INGRESO" and request.form.get(
                    'tipo_registro') == "INGRESO":
                flash('Debe registrar una SALIDA antes de registrar un nuevo INGRESO.')
                return redirect(url_for("asistencia"))
            if ultimo_registro and ultimo_registro.tipo_registro == "SALIDA" and request.form.get(
                    'tipo_registro') == "SALIDA":
                flash('Debe registrar un INGRESO antes de registrar una nueva SALIDA.')
                return redirect(url_for("asistencia"))

        tipo_registro = request.form.get('tipo_registro')
        actividad = request.form.get('actividad')

        if tipo_registro == "SALIDA" and actividad:
            flash('No se requiere actividad para registros de SALIDA.')
            return redirect(url_for("asistencia"))

        # Si el usuario está logueado como "admin", usar la fecha y hora manual del formulario
        if current_user.is_authenticated and current_user.rol == "admin":
            fecha_manual = request.form.get('fecha')
            hora_manual = request.form.get('hora')
            asistencia = Aistencia(
                dni=dni,
                tipo_registro=tipo_registro,
                actividad=actividad if tipo_registro != "SALIDA" else None,
                hora=hora_manual,
                fecha=datetime.strptime(fecha_manual, '%Y-%m-%d').date()
            )
        else:
            # Sumar un minuto a la hora si es un INGRESO
            if tipo_registro == "INGRESO":
                hora_mas_un_minuto = (hora_actual_buenos_aires + timedelta(minutes=3)).strftime('%H:%M')
            else:
                hora_mas_un_minuto = hora_actual_str

            asistencia = Aistencia(
                dni=dni,
                tipo_registro=tipo_registro,
                actividad=actividad,
                hora=hora_mas_un_minuto,
                fecha=fecha_actual
            )

        db.session.add(asistencia)
        db.session.commit()
        flash('Registro cargado exitosamente')
        return redirect(url_for("asistencia"))

    # Calcular la fecha y hora de hace 24 horas
    hace_24_horas = fecha_actual - timedelta(days=1)

    subquery = db.session.query(
        Aistencia.dni,
        func.max(Aistencia.id_asistencia).label("max_id")
    ).group_by(Aistencia.dni).subquery()

    asistencias_ingreso = db.session.query(Aistencia).join(
        subquery, Aistencia.id_asistencia == subquery.c.max_id
    ).filter(
        Aistencia.tipo_registro == "INGRESO",
        Aistencia.fecha >= hace_24_horas
    ).all()

    if current_user.is_authenticated and current_user.rol == "admin":
        # Admin ve todos los registros de asistencia
        asistencia_general = Aistencia.query.all()
    elif current_user.is_authenticated:
        # Usuario no administrador ve solo sus registros basados en legajo_numero
        asistencia_general = db.session.query(Aistencia).join(Bomberos, Bomberos.dni == Aistencia.dni).filter(
            Bomberos.legajo_numero == current_user.numero_legajo
        ).all()
    else:
        # Usuario no autenticado no ve registros
        asistencia_general = []

    # Obtener lista de bomberos para otros propósitos
    bomberos = Bomberos.query.order_by(Bomberos.legajo_numero).all()

    return render_template('asistencia.html', asistencias=asistencias_ingreso,
                           bravo=bomberos, asistencias_general=asistencia_general)

#----------------------------------------------
@app.route('/editar_asistencia/<int:id>', methods=['GET', 'POST'])
def editar_asistencia(id):
    asistencia = Aistencia.query.get_or_404(id)

    if request.method == 'POST':
        # Actualizar los datos del registro de asistencia
        asistencia.dni = request.form['dni']
        asistencia.tipo_registro = request.form['tipo_registro']
        asistencia.actividad = request.form['actividad']

        # Actualizar el campo de fecha
        fecha_manual = request.form.get('fecha')
        if fecha_manual:
            asistencia.fecha = datetime.strptime(fecha_manual, '%Y-%m-%d').date()


        # Actualizar el campo de hora
        hora_manual = request.form.get('hora')
        if hora_manual:
            asistencia.hora = hora_manual




        try:
            db.session.commit()
            flash('Registro actualizado correctamente', 'success')
            return redirect(url_for('asistencia'))
        except:
            db.session.rollback()
            flash('Hubo un error al actualizar el registro', 'danger')

    return render_template('editar_asistencia.html', asistencia=asistencia)
#----------------------------------------------
@app.route('/eliminar_asistencia/<int:id>', methods=['POST'])
def eliminar_asistencia(id):
    # Buscar el registro de asistencia por su ID
    asistencia = Aistencia.query.get_or_404(id)

    # Eliminar el registro de la base de datos
    try:
        db.session.delete(asistencia)
        db.session.commit()
        flash('Registro eliminado correctamente', 'success')
    except:
        db.session.rollback()
        flash('Hubo un error al eliminar el registro', 'danger')

    # Redirigir a la página de asistencia
    return redirect(url_for('asistencia'))

#----------------------------------------------


#----------------------------------------------CONTROL AUTOMOTORES----------------------------------------------

@app.route('/automotores', methods=['GET', 'POST'])
@login_required
def automotores():
    fecha_actual = datetime.now(app.config['TIMEZONE']).date()
    hora_actual = datetime.now(app.config['TIMEZONE']).strftime('%H:%M')
    if request.method == 'POST':
        if 'control_automotores' in request.form:

            control = ControlAutomotor(
                numero_legajo=current_user.numero_legajo,
                nombre_unidad=request.form.get('nombre_unidad'),
                fecha=fecha_actual,
                hora=hora_actual,
                bateria=request.form.get('bateria'),
                odometro=request.form.get('odometro'),
                combustible=request.form.get('combustible'),
                acite_motor=request.form.get('aceite_motor'),
                agua_radiador=request.form.get('agua_radiador'),
                liq_freno=request.form.get('liq_freno'),
                neumaticos=request.form.get('neumaticos'),
                frenos=request.form.get('frenos'),
                direccion=request.form.get('direccion'),
                luces_baja=request.form.get('luces_baja'),
                luces_alta=request.form.get('luces_alta'),
                balizas=request.form.get('balizas'),
                estrobos=request.form.get('estrobos'),
                sirena=request.form.get('sirena'),
                equipo_base=request.form.get('equipo_base'),
                limpieza_interior=request.form.get('limpieza_interior'),
                limpieza_exterior=request.form.get('limpieza_exterior'),
                puesta_marcha=request.form.get('puesta_marcha'),
                agua_tanque=request.form.get('agua_tanque'),
                observaciones=request.form.get('observaciones')
            )

            db.session.add(control)
            db.session.commit()
            flash('Control del automotor registrado exitosamente.')
            return redirect(url_for('automotores'))


        if 'control_kit' in request.form:
            control_kit = ControlKit(
                numero_legajo=current_user.numero_legajo,
                nombre_unidad=request.form.get('nombre_unidad_kit'),
                fecha=fecha_actual,
                hora=hora_actual,
                nivel_aceite=request.form.get('nivel_aceite'),
                combustible=request.form.get('combustible_kit'),
                bidon_nafta=request.form.get('bidon_nafta'),
                agua_tanque=request.form.get('agua_tanque_kit'),
                aceite_motor=request.form.get('aceite_motor_kit'),
                marcha=request.form.get('marcha'),
                novedades=request.form.get('novedades')
            )

            db.session.add(control_kit)
            db.session.commit()
            flash('Control del kit forestal registrado exitosamente.')

        return redirect(url_for('automotores'))

    controles = ControlAutomotor.query.order_by(ControlAutomotor.fecha.desc(), ControlAutomotor.hora.desc()).all()
    controles_kit = ControlKit.query.order_by(ControlKit.fecha.desc(), ControlKit.hora.desc()).all()
    return render_template('automotores.html', controles=controles, controles_kit=controles_kit)




#-------------------------------------CENTRALISTAS HORARIOS------------------------------------------


@app.route('/comunicaciones', methods=['GET', 'POST'])
def centralistas():
    tz_buenos_aires = pytz.timezone('America/Argentina/Buenos_Aires')
    fecha_actual = datetime.now(tz_buenos_aires).date()
    mes_actual = datetime.now(tz_buenos_aires).strftime('%Y-%m')
    hora_actual_utc = datetime.now(timezone('UTC'))
    hora_actual_buenos_aires = hora_actual_utc.astimezone(app.config['TIMEZONE'])
    hora_actual_str = hora_actual_buenos_aires.strftime('%H:%M')
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    print(client_ip)
    if not (current_user.is_authenticated and (current_user.rol == "admin" or current_user.rol == "automotor")):
        if client_ip not in INSTITUTION_IP:
            return redirect(url_for("error_red"))

    if request.method == 'POST':
        dni = request.form.get('dni')
        agente_existente = Bomberos.query.filter_by(dni=dni).first()

        if not agente_existente:
            flash('No se puede registrar la asistencia. El DNI no está registrado.')
            return redirect(url_for("centralistas"))

        # Verificar último registro de asistencia
        ultimo_registro = Centralistas_horarios.query.filter_by(dni=dni).order_by(
            Centralistas_horarios.id_asistencia.desc()).first()

     #   if ultimo_registro and ultimo_registro.tipo_registro == "INGRESO" and request.form.get('tipo_registro') == "INGRESO":
     #       flash('Debe registrar una SALIDA antes de registrar un nuevo INGRESO.')
     #       return redirect(url_for("centralistas"))
#
        tipo_registro = request.form.get('tipo_registro')

        # Asistencia según el rol del usuario
        if current_user.is_authenticated and current_user.rol == "admin":
            fecha_manual = request.form.get('fecha')
            hora_manual = request.form.get('hora')
            asistencia = Centralistas_horarios(
                dni=dni,
                tipo_registro=tipo_registro,
                hora=hora_manual,
                fecha=datetime.strptime(fecha_manual, '%Y-%m-%d').date()
            )
        else:
            asistencia = Centralistas_horarios(
                dni=dni,
                tipo_registro=tipo_registro,
                hora=hora_actual_str,
                fecha=fecha_actual
            )

        db.session.add(asistencia)
        db.session.commit()
        flash('Registro cargado exitosamente')
        return redirect(url_for("centralistas"))

    # Ejecutar la consulta SQL para obtener las horas trabajadas por mes para cada centralista
    registros = db.session.execute(text('''
        WITH Ordenados AS (
            SELECT
                dni,
                fecha,
                hora,
                tipo_registro,
                id_asistencia,
                LAG(tipo_registro) OVER (PARTITION BY dni ORDER BY fecha, hora) AS registro_anterior,
                LAG(fecha) OVER (PARTITION BY dni ORDER BY fecha, hora) AS fecha_anterior,
                LAG(hora) OVER (PARTITION BY dni ORDER BY fecha, hora) AS hora_anterior
            FROM
                Centralistas_horarios
        ),
        Pares AS (
            SELECT
                dni,
                strftime('%Y-%m', fecha) AS mes_anio,
                fecha_anterior AS fecha_ingreso,
                hora_anterior AS hora_ingreso,
                fecha AS fecha_salida,
                hora AS hora_salida,
                (julianday(fecha || ' ' || hora) - julianday(fecha_anterior || ' ' || hora_anterior)) * 24 AS horas_trabajadas
            FROM
                Ordenados
            WHERE
                tipo_registro = 'SALIDA' AND registro_anterior = 'INGRESO'
        )
        SELECT
            p.dni,
            b.apellido,
            p.mes_anio,
            SUM(p.horas_trabajadas) AS total_horas
        FROM
            Pares p
        JOIN
            Bomberos b ON p.dni = b.dni
        WHERE
            p.mes_anio = :mes_actual  -- Filtrar por el mes en curso
        GROUP BY
            p.dni, b.apellido, p.mes_anio
        ORDER BY
            p.mes_anio;
    '''), {'mes_actual': mes_actual}).fetchall()

    # Convertir los datos a un formato que sea fácil de manejar en el gráfico
    data = {}
    for row in registros:
        dni, apellido, mes_anio, total_horas = row
        if apellido not in data:
            data[apellido] = {}
        data[apellido][mes_anio] = total_horas

    # Mostrar las asistencias del día
    hace_24_horas = fecha_actual - timedelta(hours=24)
    asistencias_del_dia = Centralistas_horarios.query.filter(Centralistas_horarios.fecha >= hace_24_horas).all()
    asistencias_general = Centralistas_horarios.query.all()
    bomberos = Bomberos.query.order_by(Bomberos.legajo_numero).all()

    return render_template('comunicaciones.html', asistencias=asistencias_del_dia, bravo=bomberos,
                           asistencias_general=asistencias_general, data=data, mes_actual=mes_actual)





#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
@app.route('/salidas', methods=['GET', 'POST'])
@login_required
def salidas():
    if request.method == 'POST':
        fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d').date()
        hora = datetime.strptime(request.form['hora'], '%H:%M').time()
        unidad = request.form['unidad']
        tipo_alarma = request.form['tipo_alarma']
        numero_alarma = request.form['numero_alarma']
        a_cargo = request.form['a_cargo']
        chofer = request.form['chofer']
        dotacion = request.form['dotacion']
        qth = request.form['qth']
        operador = request.form['operador']
        bros_base = request.form['bros_base']
        jefe_guardia = request.form['jefe_guardia']
        observaciones = request.form.get('observaciones', '')  # Agregar esta línea
        nueva_salida = Salida(fecha=fecha, hora=hora,
                              unidad=unidad,
                              tipo_alarma=tipo_alarma,
                              numero_alarma=numero_alarma,
                              a_cargo=a_cargo,
                              chofer=chofer,
                              dotacion=dotacion,
                              qth=qth,
                              operador=operador,
                              bros_base=bros_base,
                              jefe_guardia=jefe_guardia,
                              observaciones=observaciones)
        db.session.add(nueva_salida)
        db.session.commit()

        flash('Salida registrada exitosamente', 'success')
        return redirect(url_for('salidas'))

    salidas = Salida.query.all()
    tipos_alarma = [salida.tipo_alarma for salida in salidas]
    conteo_alarmas = dict(Counter(tipos_alarma))

    # Convertir las claves y valores de conteo_alarmas a listas
    return render_template(
        'salidas.html',
        salidas=salidas,
        conteo_alarmas_labels=list(conteo_alarmas.keys()),
        conteo_alarmas_data=list(conteo_alarmas.values())
    )






#-------------------------------------------------------------------------------------------

@app.route('/salidas/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_salida(id):
    # Buscar la salida en la base de datos
    salida = Salida.query.get_or_404(id)

    if request.method == 'POST':
        try:
            # Convertir la fecha y la hora de los formularios en los objetos correctos
            #salida.fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d').date()
            #salida.hora = datetime.strptime(request.form['hora'], '%H:%M').time()

            # Actualizar los demás campos
            salida.fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d').date()
            salida.hora = datetime.strptime(request.form['hora'], '%H:%M').time()
            salida.unidad = request.form['unidad']
            salida.tipo_alarma = request.form['tipo_alarma']
            salida.numero_alarma = int(request.form['numero_alarma'])
            salida.a_cargo = request.form['a_cargo']
            salida.chofer = request.form['chofer']
            salida.dotacion = request.form['dotacion']
            salida.qth = request.form['qth']
            salida.operador=request.form['operador']
            salida.bros_base=request.form['bros_base']
            salida.jefe_guardia=request.form['jefe_guardia']
            salida.observaciones = request.form.get('observaciones', '')

            # Guardar los cambios
            db.session.commit()
            flash('La salida ha sido actualizada exitosamente', 'success')
            return redirect(url_for('salidas'))

        except Exception as e:
            flash(f'Ocurrió un error al actualizar la salida: {str(e)}', 'danger')
            db.session.rollback()

    # Mostrar el formulario con los valores actuales de la salida
    return render_template('editar_salidas.html', salida=salida)

#-------------------------------------------------------------------------------------------

@app.route('/llegadas', methods=['GET', 'POST'])
@login_required
def llegadas():
    if request.method == 'POST':
        fecha = request.form.get('fecha')
        unidad = request.form.get('unidad')
        hora_salida = request.form.get('hora_salida')
        hora_llegada = request.form.get('hora_llegada')
        novedades = request.form.get('novedades')
        numero_alarma = request.form.get('numero_alarma')
        a_cargo = request.form.get('a_cargo')

        # Convertir los campos de fecha y hora a objetos datetime
        fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        hora_salida = datetime.strptime(hora_salida, '%H:%M').time()
        hora_llegada = datetime.strptime(hora_llegada, '%H:%M').time()

        nueva_llegada = Llegada(fecha=fecha,
                                unidad=unidad,
                                hora_salida=hora_salida,
                                hora_llegada=hora_llegada,
                                novedades=novedades,
                                numero_alarma=numero_alarma,
                                a_cargo=a_cargo)

        try:
            db.session.add(nueva_llegada)
            db.session.commit()
            flash("Llegada registrada exitosamente", "success")
        except Exception as e:
            flash(f"Error al registrar llegada: {str(e)}", "danger")

        return redirect(url_for('llegadas'))

    # Consulta de llegadas para mostrar en la tabla
    llegadas = Llegada.query.order_by(desc(Llegada.fecha)).all()
    return render_template('llegadas.html', llegadas=llegadas)
#-------------------------------------------------------------------------------------------
@app.route('/editar_llegada/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_llegada(id):
    llegada = Llegada.query.get_or_404(id)

    if request.method == 'POST':
        llegada.unidad = request.form.get('unidad')
        llegada.numero_alarma = request.form['numero_alarma']
        llegada.a_cargo = request.form['a_cargo']
        llegada.novedades = request.form.get('novedades')

        # ✅ Estos estaban comentados, es necesario incluirlos si se muestran en el formulario
        llegada.hora_salida = datetime.strptime(request.form['hora_salida'], '%H:%M').time()


        llegada.hora_llegada = datetime.strptime(request.form['hora_llegada'], '%H:%M').time()

        try:
            db.session.commit()
            flash("Llegada actualizada con éxito", "success")
        except Exception as e:
            flash(f"Error al actualizar la llegada: {str(e)}", "danger")

        return redirect(url_for('llegadas'))

    return render_template('editar_llegadas.html', llegada=llegada)



#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
@app.route('/asistencia_dia_semana')
def asistencia_dia_semana():
    fecha_hace_7_dias = datetime.now() - timedelta(days=7)

    # Consultar la cantidad de ingresos por bombero en la última semana
    asistencias_por_bombero = (
        db.session.query(
            Aistencia.dni.label("bombero"),
            func.count(Aistencia.id_asistencia).label("cantidad")
        )
        .filter(Aistencia.fecha >= fecha_hace_7_dias)
        .filter(Aistencia.tipo_registro == "INGRESO")  # Solo registros de tipo "INGRESO"
        .group_by(Aistencia.dni)
        .order_by(func.count(Aistencia.id_asistencia).desc())  # Ordenado por más ingresos
        .all()
    )

    # Convertir los resultados a un formato JSON para el gráfico
    data = {
        "labels": [registro[0] for registro in asistencias_por_bombero],  # DNI de los bomberos
        "values": [registro[1] for registro in asistencias_por_bombero]   # Cantidad de ingresos
    }

    return jsonify(data)
#----------------------------------------------------------------
@app.route('/asistencia_por_actividad')
def asistencia_por_actividad():
    # Filtra asistencias de los últimos 7 días
    fecha_hace_7_dias = datetime.now() - timedelta(days=7)
    asistencias_por_actividad = (
        db.session.query(
            Aistencia.actividad.label("actividad"),  # Tipo de actividad
            func.count(Aistencia.id_asistencia).label("cantidad")
        )
        .filter(Aistencia.fecha >= fecha_hace_7_dias)
        .filter(Aistencia.tipo_registro == "INGRESO")  # Solo asistencias de tipo "INGRESO"
        .group_by("actividad")
        .order_by("cantidad")
        .all()
    )

    # Convierte los resultados a un formato JSON para el gráfico
    data = {
        "labels": [registro[0] for registro in asistencias_por_actividad],
        "values": [registro[1] for registro in asistencias_por_actividad]
    }
    return jsonify(data)

#------------------------------------------------------------------------------------------------
@app.route('/403')
def error_red():
    return render_template('403.html')

#------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------
@app.route('/control_materiales')
@login_required
def control_materiales():
    return render_template('control_materiales.html')
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
@app.route('/materiales_r1', methods=['GET', 'POST'])
@login_required
def materiales_r1():
    tz_buenos_aires = pytz.timezone('America/Argentina/Buenos_Aires')

    fecha_actual = datetime.now(tz_buenos_aires).date()

    # Obtener la hora actual en Buenos Aires
    hora_actual_utc = datetime.now(timezone('UTC'))
    hora_actual_buenos_aires = hora_actual_utc.astimezone(app.config['TIMEZONE'])

    # Convertir la hora a un objeto 'time' de Python
    hora_actual_str = hora_actual_buenos_aires.strftime('%H:%M')
    hora_actual_obj = datetime.strptime(hora_actual_str, '%H:%M').time()

    if request.method == 'POST':
        if 'materiales_r1' in request.form:
            materiales = MaterialesR1(
                numero_legajo=current_user.numero_legajo,
                fecha=fecha_actual,
                hora=hora_actual_obj,
                observaciones=request.form.get('observaciones'),
                cinta_de_vallado=request.form.get('cinta_de_vallado'),
                alcohol_en_gel=request.form.get('alcohol_en_gel'),
                llave_de_ascensor=request.form.get('llave_de_ascensor'),
                herramienta_multiproposito_manual=request.form.get('herramienta_multiproposito_manual'),
                bateria_luz=request.form.get('bateria_luz'),
                mapa_vcp=request.form.get('mapa_vcp'),
                llave_del_11=request.form.get('llave_del_11'),
                par_de_guantes_de_rescate=request.form.get('par_de_guantes_de_rescate'),
                kit_balizas=request.form.get('kit_balizas'),
                extintor_1k=request.form.get('extintor_1k'),
                tubo_de_oxigeno=request.form.get('tubo_de_oxigeno'),
                gato=request.form.get('gato'),
                caja_guantes_nitrilo=request.form.get('caja_guantes_nitrilo'),

                luz_de_escena=request.form.get('luz_de_escena'),
                conos=request.form.get('conos'),
                colcha=request.form.get('colcha'),
                estabilizadores=request.form.get('estabilizadores'),
                bolso_cubre_parantes=request.form.get('bolso_cubre_parantes'),
                cojinetes_inflables=request.form.get('cojinetes_inflables'),
                consola_de_comando_dual=request.form.get('consola_de_comando_dual'),
                bolso_con_las_mangueras=request.form.get('bolso_con_las_mangueras'),
                tubo=request.form.get('tubo'),
                mochila_de_juguetes=request.form.get('mochila_de_juguetes'),
                bolso_prehospitalario=request.form.get('bolso_prehospitalario'),
                bolso_de_trauma=request.form.get('bolso_de_trauma'),
                bolso_de_parto=request.form.get('bolso_de_parto'),
                chaleco_extraccion_adulto=request.form.get('chaleco_extraccion_adulto'),
                chaleco_extraccion_pediatric=request.form.get('chaleco_extraccion_pediatric'),
                bolso_de_ferulas_semi_rigidas=request.form.get('bolso_de_ferulas_semi_rigidas'),
                bolso_de_airbag=request.form.get('bolso_de_airbag'),
                valija_de_cubre_airbag=request.form.get('valija_de_cubre_airbag'),
                equipos_de_bioseguridad=request.form.get('equipos_de_bioseguridad'),
                sierra_sable=request.form.get('sierra_sable'),

                techo_escalera=request.form.get('techo_escalera'),
                tablas_espinal_largas=request.form.get('tablas_espinal_largas'),
                masa=request.form.get('masa'),
                hooligans=request.form.get('hooligans'),
                trancha_mediana=request.form.get('trancha_mediana'),
                cunas=request.form.get('cunas'),
                cuña_escalonada=request.form.get('cuña_escalonada'),
                tabla_espinal_mediana=request.form.get('tabla_espinal_mediana'),
                tabla_espinal_chica=request.form.get('tabla_espinal_chica'),
                holomatro=request.form.get('holomastro'),
                expansor=request.form.get('expansor'),
                multipropósito=request.form.get('multipropósito'),
                cizalla=request.form.get('cizalla'),
                ram=request.form.get('ram'),
                bolsa_de_aserrin=request.form.get('bolsa_de_aserrin'),
                barreta_chica=request.form.get('barreta_chica'),
                extintor_5k=request.form.get('extintor_5k'),
                bidon_nafta=request.form.get('bidon_nafta')
            )

            db.session.add(materiales)
            db.session.commit()
            flash('Registro de materiales R1 realizado exitosamente.')
            return redirect(url_for('materiales_r1'))

    materialesr1 = MaterialesR1.query.all()

    return render_template('materiales_r1.html',materialesr1=materialesr1)

#------------------------------------------------------------------------------------------------
@app.route('/control_bolso_r1', methods=['GET', 'POST'])
@login_required
def control_bolso_r1():
    tz_buenos_aires = pytz.timezone('America/Argentina/Buenos_Aires')

    fecha_actual = datetime.now(tz_buenos_aires).date()

    # Obtener la hora actual en Buenos Aires
    hora_actual_utc = datetime.now(timezone('UTC'))
    hora_actual_buenos_aires = hora_actual_utc.astimezone(app.config['TIMEZONE'])

    # Convertir la hora a un objeto 'time' de Python
    hora_actual_str = hora_actual_buenos_aires.strftime('%H:%M')
    hora_actual_obj = datetime.strptime(hora_actual_str, '%H:%M').time()

    if request.method == 'POST':
        numero_legajo = current_user.numero_legajo
        estado_bolso = request.form['estado_bolso']  # 'OK' o 'X'
        observaciones = request.form.get('observaciones', '')

        nuevo_registro = ControlBolsoR1(
            fecha=fecha_actual,
            hora=hora_actual_obj,
            numero_legajo=numero_legajo,
            estado_bolso=estado_bolso,
            observaciones=observaciones
        )
        db.session.add(nuevo_registro)
        db.session.commit()
        flash('Registro de materiales R1 realizado exitosamente.')

        return redirect(url_for('control_bolso_r1'))

    registros = ControlBolsoR1.query.order_by(ControlBolsoR1.fecha.desc(), ControlBolsoR1.hora.desc()).all()
    return render_template('control_bolso_r1.html', registros=registros)
#--------------
#------------------------------------------------------------------------------------------------



@app.route('/materiales_b3', methods=['GET', 'POST'])
@login_required
def materiales_b3():
    tz_buenos_aires = pytz.timezone('America/Argentina/Buenos_Aires')

    fecha_actual = datetime.now(tz_buenos_aires).date()

    # Obtener la hora actual en Buenos Aires
    hora_actual_utc = datetime.now(timezone('UTC'))
    hora_actual_buenos_aires = hora_actual_utc.astimezone(app.config['TIMEZONE'])

    # Convertir la hora a un objeto 'time' de Python
    hora_actual_str = hora_actual_buenos_aires.strftime('%H:%M')
    hora_actual_obj = datetime.strptime(hora_actual_str, '%H:%M').time()

    if request.method == 'POST':

        observaciones = request.form.get('observaciones')
        camara_termica = request.form.get('camara_termica')
        pistola_termica = request.form.get('pistola_termica')
        reflector_portatil = request.form.get('reflector_portatil')
        cinta_de_vallado = request.form.get('cinta_de_vallado')
        alcohol_en_gel = request.form.get('alcohol_en_gel')
        matafuego_5kg = request.form.get('matafuego_5kg')
        kit_balizas = request.form.get('kit_balizas')
        plano_de_vcp = request.form.get('plano_de_vcp')
        lanza_nh_2 = request.form.get('lanza_nh_2')
        lanzas_nh_1medio = request.form.get('lanzas_nh_1medio')  # Cambio de nombre
        filtro_manguerote = request.form.get('filtro_manguerote')
        llave_stz_manguerote = request.form.get('llave_stz_manguerote')
        llave_nh = request.form.get('llave_nh')
        halligan = request.form.get('halligan')
        era_con_mascara = request.form.get('era_con_mascara')
        y_stz = request.form.get('y_stz')
        conos = request.form.get('conos')
        acople_dinnem_stz = request.form.get('acople_dinnem_stz')
        reductor_stz_ww_2medio_a_1medio = request.form.get('reductor_stz_ww_2medio_a_1medio')
        reductor_stz_a_nh_1medio = request.form.get('reductor_stz_a_nh_1medio')
        reductor_stz_a_nh_1 = request.form.get('reductor_stz_a_nh_1')
        reductor_stz_2_a_stz_1medio = request.form.get('reductor_stz_2_a_stz_1medio')
        reductor_stz_2_a_nh_1medio = request.form.get('reductor_stz_2_a_nh_1medio')
        reductor_stz_2_a_nh_1 = request.form.get('reductor_stz_2_a_nh_1')
        reductor_stz_2_a_stz_1 = request.form.get('reductor_stz_2_a_stz_1')
        acople_din_stz = request.form.get('acople_din_stz')
        acople_stz_a_nh_2 = request.form.get('acople_stz_a_nh_2')
        llave_stz = request.form.get('llave_stz')
        desvanadera = request.form.get('desvanadera')
        pertiga = request.form.get('pertiga')
        manguerote = request.form.get('manguerote')
        escalera = request.form.get('escalera')
        linea_nh_1medio = request.form.get('linea_nh_1medio')
        linea_nh_2 = request.form.get('linea_nh_2')
        linea_stz_1medio = request.form.get('linea_stz_1medio')
        linea_stz_2 = request.form.get('linea_stz_2')
        bolso_prehospitalario = request.form.get('bolso_prehospitalario')
        columna_hidrante = request.form.get('columna_hidrante')
        trancha = request.form.get('trancha')

        nuevo_registro = MaterialesB3(
            fecha=fecha_actual,
            hora=hora_actual_obj,
            numero_legajo=current_user.numero_legajo,
            observaciones=observaciones,
            camara_termica=camara_termica,
            pistola_termica=pistola_termica,
            reflector_portatil=reflector_portatil,
            cinta_de_vallado=cinta_de_vallado,
            alcohol_en_gel=alcohol_en_gel,
            matafuego_5kg=matafuego_5kg,
            kit_balizas=kit_balizas,
            plano_de_vcp=plano_de_vcp,
            lanza_nh_2=lanza_nh_2,
            lanzas_nh_1medio=lanzas_nh_1medio,
            filtro_manguerote=filtro_manguerote,
            llave_stz_manguerote=llave_stz_manguerote,
            llave_nh=llave_nh,
            halligan=halligan,
            era_con_mascara=era_con_mascara,
            y_stz=y_stz,
            conos=conos,
            acople_dinnem_stz=acople_dinnem_stz,
            reductor_stz_ww_2medio_a_1medio=reductor_stz_ww_2medio_a_1medio,
            reductor_stz_a_nh_1medio=reductor_stz_a_nh_1medio,
            reductor_stz_a_nh_1=reductor_stz_a_nh_1,
            reductor_stz_2_a_stz_1medio=reductor_stz_2_a_stz_1medio,
            reductor_stz_2_a_nh_1medio=reductor_stz_2_a_nh_1medio,
            reductor_stz_2_a_nh_1=reductor_stz_2_a_nh_1,
            reductor_stz_2_a_stz_1=reductor_stz_2_a_stz_1,
            acople_din_stz=acople_din_stz,
            acople_stz_a_nh_2=acople_stz_a_nh_2,
            llave_stz=llave_stz,
            desvanadera=desvanadera,
            pertiga=pertiga,
            manguerote=manguerote,
            escalera=escalera,
            linea_nh_1medio=linea_nh_1medio,
            linea_nh_2=linea_nh_2,
            linea_stz_1medio=linea_stz_1medio,
            linea_stz_2=linea_stz_2,
            bolso_prehospitalario=bolso_prehospitalario,
            columna_hidrante=columna_hidrante,
            trancha=trancha
        )

        try:
            db.session.add(nuevo_registro)
            db.session.commit()
            flash('Registro guardado exitosamente.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar el registro: {str(e)}', 'danger')

        return redirect(url_for('materiales_b3'))

    registros = MaterialesB3.query.all()
    return render_template('materiales_b3.html', registros=registros)

#------------------------------------------------------------------------------------------------
@app.route('/control_bolso_b3', methods=['GET', 'POST'])
@login_required
def control_bolso_b3():
    tz_buenos_aires = pytz.timezone('America/Argentina/Buenos_Aires')

    fecha_actual = datetime.now(tz_buenos_aires).date()

    # Obtener la hora actual en Buenos Aires
    hora_actual_utc = datetime.now(timezone('UTC'))
    hora_actual_buenos_aires = hora_actual_utc.astimezone(app.config['TIMEZONE'])

    # Convertir la hora a un objeto 'time' de Python
    hora_actual_str = hora_actual_buenos_aires.strftime('%H:%M')
    hora_actual_obj = datetime.strptime(hora_actual_str, '%H:%M').time()

    if request.method == 'POST':
        numero_legajo = current_user.numero_legajo
        estado_bolso = request.form['estado_bolso']  # 'OK' o 'X'
        observaciones = request.form.get('observaciones', '')

        nuevo_registro = ControlBolsoB3(
            fecha=fecha_actual,
            hora=hora_actual_obj,
            numero_legajo=numero_legajo,
            estado_bolso=estado_bolso,
            observaciones=observaciones
        )
        db.session.add(nuevo_registro)
        db.session.commit()
        flash('Registro de materiales B3 realizado exitosamente.')

        return redirect(url_for('control_bolso_b3'))

    registros = ControlBolsoB3.query.order_by(ControlBolsoB3.fecha.desc(), ControlBolsoB3.hora.desc()).all()
    return render_template('control_bolso_b3.html', registros=registros)
#------------------------------------------------------------------------------------------------
@app.route('/materialesBF1', methods=['GET', 'POST'])
@login_required
def materialesBF1():
    tz_buenos_aires = pytz.timezone('America/Argentina/Buenos_Aires')

    fecha_actual = datetime.now(tz_buenos_aires).date()

    # Obtener la hora actual en Buenos Aires
    hora_actual_utc = datetime.now(timezone('UTC'))
    hora_actual_buenos_aires = hora_actual_utc.astimezone(app.config['TIMEZONE'])

    # Convertir la hora a un objeto 'time' de Python
    hora_actual_str = hora_actual_buenos_aires.strftime('%H:%M')
    hora_actual_obj = datetime.strptime(hora_actual_str, '%H:%M').time()

    if request.method == 'POST':
        numero_legajo = current_user.numero_legajo
        estado_bolso = request.form['estado_bolso']  # 'OK' o 'X'
        colaborador1=request.form['colaborador1']
        colaborador2 = request.form['colaborador2']
        observaciones = request.form.get('observaciones', '')

        nuevo_registro = MaterialesBF1(
            fecha=fecha_actual,
            hora=hora_actual_obj,
            numero_legajo=numero_legajo,
            estado_bolso=estado_bolso,
            colaborador1=colaborador1,
            colaborador2=colaborador2,
            observaciones=observaciones
        )
        db.session.add(nuevo_registro)
        db.session.commit()
        flash('Registro de materiales BF1 realizado exitosamente.')

        return redirect(url_for('materialesBF1'))

    registros = MaterialesBF1.query.order_by(MaterialesBF1.fecha.desc(), MaterialesBF1.hora.desc()).all()
    return render_template('materialesBF1.html', registros=registros)
#------------------------------------------------------------------------------
@app.route('/materialesF2', methods=['GET', 'POST'])
@login_required
def materialesF2():
    tz_buenos_aires = pytz.timezone('America/Argentina/Buenos_Aires')

    fecha_actual = datetime.now(tz_buenos_aires).date()

    # Obtener la hora actual en Buenos Aires
    hora_actual_utc = datetime.now(timezone('UTC'))
    hora_actual_buenos_aires = hora_actual_utc.astimezone(app.config['TIMEZONE'])

    # Convertir la hora a un objeto 'time' de Python
    hora_actual_str = hora_actual_buenos_aires.strftime('%H:%M')
    hora_actual_obj = datetime.strptime(hora_actual_str, '%H:%M').time()

    if request.method == 'POST':
        numero_legajo = current_user.numero_legajo
        estado_materiales = request.form['estado_bolso']  # 'OK' o 'X'
        colaborador1=request.form['colaborador1']
        colaborador2 = request.form['colaborador2']
        observaciones = request.form.get('observaciones', '')

        nuevo_registro = MaterialesF2(
            fecha=fecha_actual,
            hora=hora_actual_obj,
            numero_legajo=numero_legajo,
            estado_materiales=estado_materiales,
            colaborador1=colaborador1,
            colaborador2=colaborador2,
            observaciones=observaciones
        )
        db.session.add(nuevo_registro)
        db.session.commit()
        flash('Registro de materiales F2 realizado exitosamente.')

        return redirect(url_for('materialesF2'))

    registros = MaterialesF2.query.order_by(MaterialesF2.fecha.desc(), MaterialesF2.hora.desc()).all()
    return render_template('materialesF2.html', registros=registros)
#------------------------------------------B4-------------------------------------------------------
@app.route('/materialesB4', methods=['GET', 'POST'])
@login_required
def materialesB4():
    tz_buenos_aires = pytz.timezone('America/Argentina/Buenos_Aires')

    fecha_actual = datetime.now(tz_buenos_aires).date()

    # Obtener la hora actual en Buenos Aires
    hora_actual_utc = datetime.now(timezone('UTC'))
    hora_actual_buenos_aires = hora_actual_utc.astimezone(app.config['TIMEZONE'])

    # Convertir la hora a un objeto 'time' de Python
    hora_actual_str = hora_actual_buenos_aires.strftime('%H:%M')
    hora_actual_obj = datetime.strptime(hora_actual_str, '%H:%M').time()

    if request.method == 'POST':
        numero_legajo = current_user.numero_legajo
        estado_materiales = request.form['estado_bolso']  # 'OK' o 'X'
        colaborador1=request.form['colaborador1']
        colaborador2 = request.form['colaborador2']
        observaciones = request.form.get('observaciones', '')

        nuevo_registro = MaterialesB4(
            fecha=fecha_actual,
            hora=hora_actual_obj,
            numero_legajo=numero_legajo,
            estado_materiales=estado_materiales,
            colaborador1=colaborador1,
            colaborador2=colaborador2,
            observaciones=observaciones
        )
        db.session.add(nuevo_registro)
        db.session.commit()
        flash('Registro de materiales B4 realizado exitosamente.')

        return redirect(url_for('materialesB4'))

    registros = MaterialesB4.query.order_by(MaterialesB4.fecha.desc(), MaterialesB4.hora.desc()).all()
    return render_template('materialesB4.html', registros=registros)

#-------------------------------------------B2-----------------------------------------------------
@app.route('/materialesB2', methods=['GET', 'POST'])
@login_required
def materialesB2():
    tz_buenos_aires = pytz.timezone('America/Argentina/Buenos_Aires')

    fecha_actual = datetime.now(tz_buenos_aires).date()

    # Obtener la hora actual en Buenos Aires
    hora_actual_utc = datetime.now(timezone('UTC'))
    hora_actual_buenos_aires = hora_actual_utc.astimezone(app.config['TIMEZONE'])

    # Convertir la hora a un objeto 'time' de Python
    hora_actual_str = hora_actual_buenos_aires.strftime('%H:%M')
    hora_actual_obj = datetime.strptime(hora_actual_str, '%H:%M').time()

    if request.method == 'POST':
        numero_legajo = current_user.numero_legajo
        estado_materiales = request.form['estado_bolso']  # 'OK' o 'X'
        colaborador1=request.form['colaborador1']
        colaborador2 = request.form['colaborador2']
        observaciones = request.form.get('observaciones', '')

        nuevo_registro = MaterialesB2(
            fecha=fecha_actual,
            hora=hora_actual_obj,
            numero_legajo=numero_legajo,
            estado_materiales=estado_materiales,
            colaborador1=colaborador1,
            colaborador2=colaborador2,
            observaciones=observaciones
        )
        db.session.add(nuevo_registro)
        db.session.commit()
        flash('Registro de materiales B2 realizado exitosamente.')

        return redirect(url_for('materialesB2'))

    registros = MaterialesB2.query.order_by(MaterialesB2.fecha.desc(), MaterialesB2.hora.desc()).all()
    return render_template('materialesB2.html', registros=registros)
#------------------------------------------------------------------------------------------------
@app.route('/equipamientor1', methods=['GET', 'POST'])
@login_required
def equipamientor1():
    tz_buenos_aires = pytz.timezone('America/Argentina/Buenos_Aires')

    fecha_actual = datetime.now(tz_buenos_aires).date()

    # Obtener la hora actual en Buenos Aires
    hora_actual_utc = datetime.now(timezone('UTC'))
    hora_actual_buenos_aires = hora_actual_utc.astimezone(app.config['TIMEZONE'])

    # Convertir la hora a un objeto 'time' de Python
    hora_actual_str = hora_actual_buenos_aires.strftime('%H:%M')
    hora_actual_obj = datetime.strptime(hora_actual_str, '%H:%M').time()

    if request.method == 'POST':
        numero_legajo = current_user.numero_legajo
        estado_materiales = request.form['estado_bolso']  # 'OK' o 'X'
        colaborador1=request.form['colaborador1']
        colaborador2 = request.form['colaborador2']
        observaciones = request.form.get('observaciones', '')

        nuevo_registro = Equipamiento_R1(
            fecha=fecha_actual,
            hora=hora_actual_obj,
            numero_legajo=numero_legajo,
            estado_materiales=estado_materiales,
            colaborador1=colaborador1,
            colaborador2=colaborador2,
            observaciones=observaciones
        )
        db.session.add(nuevo_registro)
        db.session.commit()
        flash('Registro de materiales R1 realizado exitosamente.')

        return redirect(url_for('equipamientor1'))

    registros = Equipamiento_R1.query.order_by(Equipamiento_R1.fecha.desc(), Equipamiento_R1.hora.desc()).all()
    return render_template('equipamientor1.html', registros=registros)
#------------------------------------------------------------------------------------------------
@app.route('/equipamientob3', methods=['GET', 'POST'])
@login_required
def equipamientob3():
    tz_buenos_aires = pytz.timezone('America/Argentina/Buenos_Aires')

    fecha_actual = datetime.now(tz_buenos_aires).date()

    # Obtener la hora actual en Buenos Aires
    hora_actual_utc = datetime.now(timezone('UTC'))
    hora_actual_buenos_aires = hora_actual_utc.astimezone(app.config['TIMEZONE'])

    # Convertir la hora a un objeto 'time' de Python
    hora_actual_str = hora_actual_buenos_aires.strftime('%H:%M')
    hora_actual_obj = datetime.strptime(hora_actual_str, '%H:%M').time()

    if request.method == 'POST':
        numero_legajo = current_user.numero_legajo
        estado_materiales = request.form['estado_bolso']  # 'OK' o 'X'
        colaborador1=request.form['colaborador1']
        colaborador2 = request.form['colaborador2']
        observaciones = request.form.get('observaciones', '')

        nuevo_registro = Equipamiento_B3(
            fecha=fecha_actual,
            hora=hora_actual_obj,
            numero_legajo=numero_legajo,
            estado_materiales=estado_materiales,
            colaborador1=colaborador1,
            colaborador2=colaborador2,
            observaciones=observaciones
        )
        db.session.add(nuevo_registro)
        db.session.commit()
        flash('Registro de materiales B3 realizado exitosamente.')

        return redirect(url_for('equipamientob3'))

    registros = Equipamiento_B3.query.order_by(Equipamiento_B3.fecha.desc(), Equipamiento_B3.hora.desc()).all()
    return render_template('equipamientob3.html', registros=registros)
#------------------------------------------------------------------------------------------------
@app.route('/notificaciones')
@login_required
def notificaciones():
    notificaciones_usuario = Notificacion.query.filter_by(usuario_id=current_user.id).order_by(Notificacion.fecha.desc()).all()

    # Marcar como leídas las que estaban pendientes
    for noti in notificaciones_usuario:
        if not noti.leida:
            noti.leida = True
    db.session.commit()

    return render_template('notificaciones.html', notificaciones=notificaciones_usuario)
@app.context_processor
def inject_notificaciones():
    if current_user.is_authenticated:
        cantidad_no_leidas = Notificacion.query.filter_by(usuario_id=current_user.id, leida=False).count()
        return dict(notificaciones_no_leidas=cantidad_no_leidas)
    return dict(notificaciones_no_leidas=0)

#---------------------------------------RESPONSABLE DE AREA---------------------------------------------------------
@app.route('/responsables_area', methods=['GET', 'POST'])
@login_required
@role_required('admin')  # Solo admin puede administrar responsables
def responsables_area():
    if request.method == 'POST':
        area = request.form['area']
        usuario_id = request.form['usuario_id']

        # Evitar duplicados por área
        existente = ResponsableArea.query.filter_by(area=area).first()
        if existente:
            flash('Ya existe un responsable asignado a esta área.', 'warning')
        else:
            nuevo = ResponsableArea(area=area, usuario_id=usuario_id)
            db.session.add(nuevo)
            db.session.commit()
            flash('Responsable asignado correctamente.', 'success')

        return redirect(url_for('responsables_area'))

    responsables = ResponsableArea.query.all()
    usuarios = User.query.order_by(User.name).all()
    return render_template('responsables_area.html', responsables=responsables, usuarios=usuarios)

#----------------------------------------ELIMINAR RESPONSABLE DE AREA--------------------------------------------------------
@app.route('/responsables_area/eliminar/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def eliminar_responsable(id):
    responsable = ResponsableArea.query.get_or_404(id)
    db.session.delete(responsable)
    db.session.commit()
    flash('Responsable eliminado correctamente.', 'success')
    return redirect(url_for('responsables_area'))

#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True, port=8080)  # Cambia 8080 al puerto que prefieras
