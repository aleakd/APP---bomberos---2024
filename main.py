from flask import Flask, render_template, request, redirect, url_for, flash, jsonify,send_from_directory, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from functools import wraps
import pytz

from werkzeug.middleware.proxy_fix import ProxyFix

from pytz import timezone
import os
from werkzeug.utils import secure_filename
from datetime import datetime, date, timedelta

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
    dni  = db.Column(db.Integer)
    tipo_registro = db.Column(db.String(10))
    fecha = db.Column(db.Date)
    hora = db.Column(db.String(10))




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

def role_required(rol):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.rol != rol:
                flash('No tienes permiso para acceder a esta página.')
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

            dni_pdf = request.files("dni_pdf")
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

#----------------------------------------------#--------------CAMBIOS DE GUARDIA--------------------------------
@app.route('/cambiosguardia', methods=['GET', 'POST'])
@login_required
def cambiosguardia():
    if request.method == 'POST':
        if 'registrar_cambio_guardia' in request.form:
            numero_legajo = current_user.numero_legajo
            fecha_solicitud = request.form.get("fecha_solicitud")
            rango_horario = request.form.get("rango_horario")
            rango_horario2 = request.form.get("rango_horario2")
            legajo_quien_cubre = request.form.get("legajo_quien_cubre")
            motivo = request.form.get("motivo")
            fecha_devolucion = request.form.get("fecha_devolucion")
            imagen = request.files.get("imagen")
            imagen_filename = None

            if imagen and allowed_file(imagen.filename):
                filename = secure_filename(imagen.filename)
                imagen_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'licencias', filename)
                os.makedirs(os.path.dirname(imagen_filename), exist_ok=True)
                imagen.save(imagen_filename)
                imagen_filename = os.path.join('uploads', 'licencias', filename)  # Guardar la ruta relativa


            nuevo_cambio = Cambios_Guardia(
                numero_legajo=numero_legajo,
                fecha_solicitud=datetime.strptime(fecha_solicitud, '%Y-%m-%d').date(),
                rango_horario=datetime.strptime(rango_horario, '%H:%M').time(),
                rango_horario2=datetime.strptime(rango_horario2, '%H:%M').time(),
                legajo_quien_cubre=legajo_quien_cubre,
                motivo=motivo,
                fecha_devolucion=datetime.strptime(fecha_devolucion, '%Y-%m-%d').date(),
                imagen=imagen_filename

            )
            db.session.add(nuevo_cambio)
            db.session.commit()
            flash("Cambio de guardia registrado exitosamente")
            return redirect(url_for("cambiosguardia"))



    cambios = Cambios_Guardia.query.all()
    apellidos = {bombero.legajo_numero: bombero.apellido for bombero in Bomberos.query.all()}
    return render_template("cambiosguardia.html", cambios=cambios, apellidos=apellidos)




#----------------------------------------------#-----------EDITAR CAMBIOS DE GUARDIA-----------------------------------
@app.route('/editar_cambio_guardia/<int:id>', methods=["GET", "POST"])
@login_required
@role_required('admin')
def editar_cambio_guardia(id):
    cambio_guardia = Cambios_Guardia.query.get_or_404(id)

    if request.method == "POST":

        cambio_guardia.legajo_quien_cubre = request.form.get("legajo_quien_cubre")
        cambio_guardia.motivo = request.form.get("motivo")
        cambio_guardia.fecha_devolucion = datetime.strptime(request.form.get("fecha_devolucion"), '%Y-%m-%d').date()
        cambio_guardia.aprovado = request.form.get("aprovado")

        db.session.commit()
        flash("Solicitud de cambio de guardia actualizada exitosamente")
        return redirect(url_for("cambiosguardia"))

    return render_template("editar_cambio_guardia.html", cambio_guardia=cambio_guardia)


#----------------------------------------------#---------ELIMINAR CAMBIO GUARDIA-------------------------------------
@app.route('/eliminar_cambio_guardia/<int:id>', methods=['POST'])
@role_required('admin')
@login_required
def eliminar_cambio_guardia(id):
    try:
        cambiog = Cambios_Guardia.query.get_or_404(id)
        db.session.delete(cambiog)
        db.session.commit()
        return jsonify({"success": True, "message": "Registro de cambio de guardia eliminado exitosamente."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Hubo un problema al eliminar el registro."}), 500

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
    provisto = Epp_provisto.query.get_or_404(id)
    if request.method == "POST":
        provisto.casco_estructural = request.form.get("casco_estructural")
        provisto.monja_estructural = request.form.get("monja_estructural")
        provisto.guantes__estructural = request.form.get("guantes_estructural")
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
    indumentaria = IndumentariaProvista.query.get_or_404(id)
    if request.method == "POST":
        indumentaria.gorra = request.form.get("gorra")
        indumentaria.gorra = request.form.get("gorra")
        indumentaria.remera_azul = request.form.get("remera_azul")
        indumentaria.pantalon_fajina = request.form.get("pantalon_fajina")
        indumentaria.borcegos = request.form.get("borcegos")
        indumentaria.rompeviento = request.form.get("rompeviento")
        indumentaria.camp_neopren = request.form.get("camp_neopren")
        indumentaria.bermuda = request.form.get("bermuda")

        # Guardar los cambios en la base de datos
        db.session.commit()
        flash("Registro actualizado exitosamente")
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

#----------------------------------------------#----------------------------------------------
@app.route('/uploads/partes/<filename>')
def download_file(filename):
    subdirectory = "partes"
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
#----------------------------------------------Asistencia#----------------------------------------------
INSTITUTION_IP = "127.0.0.1"
def calcular_horas_y_minutos_acumulados(dni):
    mes_actual = datetime.now().month
    año_actual = datetime.now().year

    # Filtrar las asistencias del usuario para el mes y año actual
    asistencias_mes = Aistencia.query.filter(
        Aistencia.dni == dni,
        Aistencia.fecha.between(
            datetime(año_actual, mes_actual, 1),
            datetime(año_actual, mes_actual + 1, 1) - timedelta(seconds=1)
        )
    ).order_by(Aistencia.fecha, Aistencia.hora).all()

    horas_acumuladas = timedelta()
    entrada_actual = None

    for asistencia in asistencias_mes:
        if asistencia.tipo_registro == "INGRESO":
            # Guarda la entrada actual para emparejar más tarde
            entrada_actual = asistencia
        elif asistencia.tipo_registro == "SALIDA" and entrada_actual:
            # Empareja la salida con la entrada actual
            salida = asistencia

            # Convertir las horas de cadena a datetime.time
            hora_entrada = datetime.strptime(entrada_actual.hora, '%H:%M').time()
            hora_salida = datetime.strptime(salida.hora, '%H:%M').time()

            # Combinar la fecha con las horas convertidas
            tiempo_entrada = datetime.combine(entrada_actual.fecha, hora_entrada)
            tiempo_salida = datetime.combine(salida.fecha, hora_salida)

            # Sumar la diferencia de tiempo entre salida e ingreso
            horas_acumuladas += tiempo_salida - tiempo_entrada

            # Restablecer la entrada actual para procesar el siguiente par
            entrada_actual = None

    # Convertir timedelta a horas y minutos
    total_horas = int(horas_acumuladas.total_seconds() // 3600)
    total_minutos = int((horas_acumuladas.total_seconds() % 3600) // 60)

    return f"{total_horas} horas y {total_minutos} minutos"


@app.route('/asistencia', methods=['GET', 'POST'])
def asistencia():
    fecha_actual = datetime.now().date()
    hora_actual_utc = datetime.now(timezone('UTC'))
    hora_actual_buenos_aires = hora_actual_utc.astimezone(app.config['TIMEZONE'])
    hora_actual_str = hora_actual_buenos_aires.strftime('%H:%M')
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    print(client_ip)
    print("esta es la IP")
    if client_ip != INSTITUTION_IP:
        # Si la IP no coincide, se niega el acceso
        abort(403,
              description="Acceso denegado: Debe estar conectado a la red de la institución para registrar asistencia.")
    print(client_ip)
    if request.method == 'POST':
        dni = request.form.get('dni')
        agente_existente = Bomberos.query.filter_by(dni=dni).first()

        if not agente_existente:
            flash('No se puede registrar la asistencia. El DNI no está registrado.')
            return redirect(url_for("acces"))

        tipo_registro = request.form.get('tipo_registro')

        asistencia = Aistencia(
            dni=dni,
            tipo_registro=tipo_registro,
            hora=hora_actual_str,
            fecha=fecha_actual
        )
        db.session.add(asistencia)
        db.session.commit()
        flash('registro cargado exitosamente')
        return redirect(url_for("index"))

    asistencias_del_dia = Aistencia.query.filter(Aistencia.fecha == fecha_actual).all()
    bomberos = Bomberos.query.order_by(Bomberos.legajo_numero).all()

    return render_template('asistencia.html', asistencias=asistencias_del_dia, bravo=bomberos)




#----------------------------------------------modificar password#----------------------------------------------




if __name__ == '__main__':
    app.run(debug=True, port=8080)  # Cambia 8080 al puerto que prefieras
