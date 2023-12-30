# -------------------------------------------------------
# Importamos extenciones
# -------------------------------------------------------
import mysql.connector
from flask import Flask, request, jsonify, session, render_template, make_response
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import time


# -------------------------------------------------------
# Definimos la clase BaseAfiliados
# -------------------------------------------------------
app = Flask(__name__)
app.secret_key = "dev"
CORS(app)  # Esto habilita CORS para todas las rutas

# -------------------------------------------------------


class BaseClinica:
    def __init__(
        self, host, user, password, database
    ):  # Inicializador con los parametros de ingreso a la BBDD
        self.conn = mysql.connector.connect(
            host=host, user=user, password=password, database=database
        )

        self.cursor = self.conn.cursor()

        # intentamos seleccionar la BBDD
        try:
            self.cursor.execute(f"USE {database}")
        except mysql.connector.Error as err:
            # Si la BBDD no existe la creamos
            if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.cursor.execute(f"CRATE DATABASE {database}")
                self.conn.database = database
            else:
                raise err

        # Una vez establecida la BBDD creamos SI NO EXISTE la tabla
        self.cursor.execute(
            """create table if not exists afiliados(
                            dni INT PRIMARY KEY,
                            nombre VARCHAR(50),
                            apellido VARCHAR(50),
                            fecha_nac VARCHAR(10),
                            email VARCHAR(70),
                            password VARCHAR (6),
                            plan VARCHAR(20),
                            foto VARCHAR(255),
                            prestador INT(3))"""
        )

        self.cursor.execute(
            """create table if not exists empresas(
                            codigo INT(3) PRIMARY KEY,
                            nombre VARCHAR(50),
                            rubro VARCHAR(30),
                            direccion VARCHAR(50),
                            mail VARCHAR(70))"""
        )

        self.cursor.execute(
            """create table if not exists usuarios(
                            dni INT PRIMARY KEY,
                            nombre VARCHAR(50),
                            apellido VARCHAR(50),
                            fecha_nac VARCHAR(10),
                            puesto VARCHAR(50),
                            contrato VARCHAR (20),
                            foto VARCHAR(255),
                            password VARCHAR(6),
                            empresa INT(3),
                            estado VARCHAR (20))"""
        )

        self.cursor.execute(
            """create table if not exists puestos(
                            codigo INT PRIMARY KEY,
                            nombre VARCHAR(50))"""
        )

        self.cursor.execute(
            """create table if not exists contratos(
                            codigo INT PRIMARY KEY,
                            tipo VARCHAR(50))"""
        )

        self.cursor.execute(
            """create table if not exists estados(
                            codigo INT PRIMARY KEY,
                            estado VARCHAR(50))"""
        )

        self.cursor.execute(
            """create table if not exists mensajes(
                            numero INT(11) PRIMARY KEY AUTO_INCREMENT,
                            fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            nombre VARCHAR(70),
                            mail VARCHAR(70),
                            mensaje TEXT)"""
        )

        self.cursor.execute(
            """CREATE VIEW if not exists cons_usuarios AS SELECT `usuarios`.`dni`, `usuarios`.`nombre`, `usuarios`.`apellido`, `usuarios`.`fecha_nac`, `usuarios`.`foto`, `empresas`.`nombre` as 'Empresa', `puestos`.`nombre` as 'Puesto', `contratos`.`tipo` as 'Contrato', `estados`.`estado` as 'Estado' FROM `usuarios`
INNER JOIN `empresas` ON `usuarios`.`empresa` = `empresas`.`codigo`
INNER JOIN `puestos` ON `usuarios`.`puesto` = `puestos`.`codigo`
INNER JOIN `contratos`ON `usuarios`.`contrato` = `contratos`.`codigo`
INNER JOIN `estados` ON `usuarios`.`estado` = `estados`.`codigo` order by `usuarios`.`dni` ASC""")

        self.cursor.execute("""create view if not exists cons_pass_usuarios as select * from usuarios""")

        self.cursor.execute("""create view if not exists cons_pass_afiliados as select * from afiliados""")

        self.conn.commit()  # Le damos confirmacion a la sentencia SQL

        # Cerramos el cursor inicial y abrimos uno nuevo con el parámetro de dictionary = True
        self.cursor.close()
        self.cursor = self.conn.cursor(dictionary=True)

    # ****************  METODOS AUXILIARES - METODOS AUXILIARES - METODOS AUXILIARES  ************************************

    # -------------------------------------------------------
    # Metodo para LOGIN de AFILIADOS
    # -------------------------------------------------------
    def login_afiliados(self, email, password):
        # Verificamos si el afiliado ya existe en la BBDD
        self.cursor.execute(f"SELECT * FROM cons_pass_afiliados WHERE email = '{email}' AND password = '{password}'")  # Busca en la BBD si esta ese combo
        afiliado_existe = (self.cursor.fetchone())  # Si el combo existe lo guarda en variable afiliado_existe

        if afiliado_existe:  # Si existe manda este mensaje

#            return True
            return afiliado_existe

    # -------------------------------------------------------
    # Metodo para LOGIN de USUARIOS
    # -------------------------------------------------------
    def login_usuarios(self, dni, password):
        # Verificamos si el usuario ya existe en la BBDD
        self.cursor.execute(f"SELECT * FROM cons_pass_usuarios WHERE dni = {dni} AND password = '{password}'")  # Busca en la BBD si esta ese combo
        usuario_existe = (self.cursor.fetchone())  # Si el combo existe lo guarda en variable usuario_existe

        if usuario_existe:  # Si existe manda este mensaje
            return True

    # -------------------------------------------------------
    # Metodo para obtener listado de tabla PUESTOS
    # -------------------------------------------------------
    def listar_puestos(self):
        self.cursor.execute("SELECT * FROM puestos")
        puestos = self.cursor.fetchall()
        return puestos

    # -------------------------------------------------------
    # Metodo para obtener listado de tabla CONTRATOS
    # -------------------------------------------------------
    def listar_contratos(self):
        self.cursor.execute("SELECT * FROM contratos")
        contratos = self.cursor.fetchall()
        return contratos

    # -------------------------------------------------------
    # Metodo para obtener listado de tabala ESTADOS
    # -------------------------------------------------------
    def listar_estados(self):
        self.cursor.execute("SELECT * FROM estados")
        estados = self.cursor.fetchall()
        return estados

    # -------------------------------------------------------
    # Metodo para agregar un MENSAJE
    # -------------------------------------------------------

    def agregar_mensaje(self, nombre, mail, mensaje):
        sql = f"INSERT INTO mensajes \
                (nombre, mail, mensaje) \
                VALUES \
                ('{nombre}', '{mail}', '{mensaje}')"

        self.cursor.execute(sql)  # El cursor ejecuta el comando SQL
        self.conn.commit()  # Confirmo la ejecucion
        return True

    # ****************  METODOS AFILIADOS - METODOS AFILIADOS - METODOS AFILIADOS  ***************************************

    # -------------------------------------------------------
    # Metodo para obtener listado de afiliados por pantalla
    # -------------------------------------------------------
    def listar_afiliados(self):
        self.cursor.execute("SELECT * FROM afiliados")
        afiliados = self.cursor.fetchall()
        return afiliados

    # ---------------------------------------------------------
    # Metodo para consultar un afiliado a partir de su dni
    # ---------------------------------------------------------
    def consultar_afiliado(self, dni):
        self.cursor.execute(
            f"SELECT * FROM afiliados WHERE dni = {dni}"
        )  # Busca en la BBD si esta ese DNI)
        return self.cursor.fetchone()  # Regresa solo ese afiliado encontrado

    # -------------------------------------------------------
    # Metodo para agregar un afiliado
    # -------------------------------------------------------

    def agregar_afiliado(self, dni, nombre, apellido, fecha_nac, plan, foto, prestador):
        # Verificamos si el afiliado ya existe en la BBDD
        self.cursor.execute(
            f"SELECT * FROM afiliados WHERE dni = {dni}"
        )  # Busca en la BBD si esta ese DNI
        afiliado_existe = (
            self.cursor.fetchone()
        )  # Si el DNI existe lo guarda en variable afiliado_existe

        if afiliado_existe:  # Si existe manda este mensaje
            print(f"AFILIADO {dni} YA EXISTE EN LOS REGISTROS!")
            return False

        sql = f"INSERT INTO afiliados \
                (dni, nombre, apellido, fecha_nac, plan, foto, prestador) \
                VALUES \
                ({dni}, '{nombre}', '{apellido}', '{fecha_nac}', '{plan}', '{foto}', {prestador})"  # Si no existe lo agrega a la tabla

        self.cursor.execute(sql)  # El cursor ejecuta el comando SQL
        self.conn.commit()  # Confirmo la ejecucion
        return True

    # ---------------------------------------------------------------------
    # Metodo para eliminar los datos de un afiliado a partir de su dni
    # ---------------------------------------------------------------------
    def eliminar_afiliado(self, dni):
        # Eliminamos un producto de la tabla a partir de su código
        self.cursor.execute(f"DELETE FROM afiliados WHERE dni = {dni}")
        self.conn.commit()
        return self.cursor.rowcount > 0

    # ----------------------------------------------------------------------
    # Metodo para modificar los datos de un afiliado a partir de su dni
    # ----------------------------------------------------------------------
    def modificar_afiliado(
        self,
        dni,
        nuevo_nombre,
        nuevo_apellido,
        nueva_fecha_nac,
        nuevo_plan,
        nueva_foto,
        nuevo_prestador,
    ):
        sql = "UPDATE afiliados SET nombre = %s, apellido = %s, fecha_nac = %s, plan = %s, foto = %s, prestador = %s WHERE dni = %s"
        valores = (
            nuevo_nombre,
            nuevo_apellido,
            nueva_fecha_nac,
            nuevo_plan,
            nueva_foto,
            nuevo_prestador,
            dni,
        )
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return self.cursor.rowcount > 0

    # ---------------------------------------------------------------------
    # Metodo para eliminar los datos de un afiliado a partir de su dni
    # ---------------------------------------------------------------------
    def eliminar_afiliado(self, dni):
        # Eliminamos un producto de la tabla a partir de su código
        self.cursor.execute(f"DELETE FROM afiliados WHERE dni = {dni}")
        self.conn.commit()
        return self.cursor.rowcount > 0

    # ****************  METODOS EMPRESA - METODOS EMPRESA - METODOS EMPRESA  *********************************************

    # ---------------------------------------------------------
    # Metodo para consultar una empresa a partir de su codigo
    # ---------------------------------------------------------
    def consultar_empresa(self, codigo):
        self.cursor.execute(
            f"SELECT * FROM empresas WHERE codigo = {codigo}"
        )  # Busca en la BBD si esta ese codigo
        return self.cursor.fetchone()  # Regresa solo ese codigo encontrado

    # -------------------------------------------------------
    # Metodo para agregar una empresa
    # -------------------------------------------------------
    def agregar_empresa(self, codigo, nombre, rubro, direccion, mail):
        # Verificamos si la empresa ya existe en la BBDD
        self.cursor.execute(
            f"SELECT * FROM empresas WHERE codigo = {codigo}"
        )  # Busca en la BBD si esta ese codigo
        empresa_existe = (
            self.cursor.fetchone()
        )  # Si el codigo existe lo guarda en variable empresa_existe

        if empresa_existe:  # Si existe manda este mensaje
            print(f"Empresa {codigo} YA EXISTE EN LOS REGISTROS!")
            return False

        sql = f"INSERT INTO empresas \
                (codigo, nombre, rubro, direccion, mail) \
                VALUES \
                ({codigo}, '{nombre}', '{rubro}', '{direccion}', '{mail}')"  # Si no existe lo agrega a la tabla

        self.cursor.execute(sql)  # El cursor ejecuta el comando SQL
        self.conn.commit()  # Confirmo la ejecucion
        return True

    # -------------------------------------------------------
    # Metodo para obtener listado de empresas por pantalla
    # -------------------------------------------------------
    def listar_empresas(self):
        self.cursor.execute("SELECT * FROM empresas")
        empresas = self.cursor.fetchall()
        return empresas

    # ----------------------------------------------------------------------
    # Metodo para modificar los datos de una empresa por su codigo
    # ----------------------------------------------------------------------
    def modificar_empresa(
        self,
        codigo,
        nuevo_nombre,
        nuevo_rubro,
        nueva_direccion,
        nuevo_mail,
    ):
        sql = "UPDATE empresas SET nombre = %s, rubro = %s, direccion = %s, mail = %s WHERE codigo = %s"
        valores = (
            nuevo_nombre,
            nuevo_rubro,
            nueva_direccion,
            nuevo_mail,
            codigo,
        )
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return self.cursor.rowcount > 0

    # ---------------------------------------------------------------------
    # Metodo para eliminar los datos de una empresa a partir de su codigo
    # ---------------------------------------------------------------------
    def eliminar_empresa(self, codigo):
        # Eliminamos una empresa de la tabla a partir de su código
        self.cursor.execute(f"DELETE FROM empresas WHERE codigo = {codigo}")
        self.conn.commit()
        return self.cursor.rowcount > 0

    # ****************  METODOS USUARIOS - METODOS USUARIOS - METODOS USUARIOS  *********************************************

    # ---------------------------------------------------------
    # Metodo para consultar un usuario a partir de su dni
    # ---------------------------------------------------------
    def consultar_usuario(self, dni):
        self.cursor.execute(
            f"SELECT * FROM usuarios WHERE dni = {dni}"
        )  # Busca en la BBD si esta ese DNI)
        return self.cursor.fetchone()  # Regresa solo ese afiliado encontrado

    # -------------------------------------------------------
    # Metodo para agregar un usuario
    # -------------------------------------------------------

    def agregar_usuario(
        self, dni, nombre, apellido, fecha_nac, puesto, contrato, foto, password, empresa, estado
    ):
        # Verificamos si el afiliado ya existe en la BBDD
        self.cursor.execute(
            f"SELECT * FROM usuarios WHERE dni = {dni}"
        )  # Busca en la BBD si esta ese DNI
        usuario_existe = (
            self.cursor.fetchone()
        )  # Si el DNI existe lo guarda en variable afiliado_existe

        if usuario_existe:  # Si existe manda este mensaje
            print(f"USUARIO {dni} YA EXISTE EN LOS REGISTROS!")
            return False

        sql = f"INSERT INTO usuarios \
                (dni, nombre, apellido, fecha_nac, puesto, contrato, foto, password, empresa, estado) \
                VALUES \
                ({dni}, '{nombre}', '{apellido}', '{fecha_nac}', '{puesto}', '{contrato}', '{foto}', '{password}', '{empresa}', '{estado}')"  # Si no existe lo agrega a la tabla

        self.cursor.execute(sql)  # El cursor ejecuta el comando SQL
        self.conn.commit()  # Confirmo la ejecucion
        return True

    # -------------------------------------------------------
    # Metodo para obtener listado de usuarios por pantalla mediante VISTA en BBDD
    # -------------------------------------------------------
    def listar_usuarios(self):
        self.cursor.execute(
            "SELECT * FROM `cons_usuarios` ORDER BY `cons_usuarios`.`dni` ASC"
        )
        usuarios = self.cursor.fetchall()
        return usuarios

    # -------------------------------------------------------
    # Metodo para obtener listado de usuarios por pantalla mediante VISTA en BBDD
    # -------------------------------------------------------
    def listar_usuarios_crudo(self):
        self.cursor.execute("SELECT * FROM `usuarios` ORDER BY `usuarios`.`dni` ASC")
        usuarios = self.cursor.fetchall()
        return usuarios

    # ----------------------------------------------------------------------
    # Metodo para modificar los datos de un usuario a partir de su dni
    # ----------------------------------------------------------------------
    def modificar_usuario(
        self,
        dni,
        nuevo_nombre,
        nuevo_apellido,
        nueva_fecha_nac,
        nuevo_puesto,
        nuevo_contrato,
        nueva_foto,
        nueva_empresa,
        nuevo_estado,
    ):
        sql = "UPDATE usuarios SET nombre = %s, apellido = %s, fecha_nac = %s, puesto = %s, contrato = %s, foto = %s, empresa = %s, estado = %s WHERE dni = %s"
        valores = (
            nuevo_nombre,
            nuevo_apellido,
            nueva_fecha_nac,
            nuevo_puesto,
            nuevo_contrato,
            nueva_foto,
            nueva_empresa,
            nuevo_estado,
            dni,
        )
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return self.cursor.rowcount > 0

    # ---------------------------------------------------------------------
    # Metodo para eliminar los datos de un usuario a partir de su dni
    # ---------------------------------------------------------------------
    def eliminar_usuario(self, dni):
        # Eliminamos un producto de la tabla a partir de su código
        self.cursor.execute(f"DELETE FROM usuarios WHERE dni = {dni}")
        self.conn.commit()
        return self.cursor.rowcount > 0


# --------------------------------------------------------------------------------------------------------------------------
# ************************************   Programa Principal   **************************************************************
# --------------------------------------------------------------------------------------------------------------------------
# Nos conectamos a la BBDD
BaseClinica = BaseClinica(host="localhost", user="root", password="", database="miapp")
# Carpeta para guardar las imagenes.
# RUTA_DESTINO = "/home/SakkarArg/mysite/static/imagenes"
RUTA_DESTINO = "./static/imagenes/"


# *************************************  COMIENZAN PROGRAMAS AUXILIARES   *********************************************************


# --------------------------------------------------------------------
# LOGIN de AFILIADOS
# --------------------------------------------------------------------
@app.route("/cons_pass_afiliados", methods=["POST"])
def login_afiliados():  # Capturo los datos que vienen del HTML
    email = request.form["email"]
    password = request.form["password"]

    # Me aseguro que el afiliado exista
    afiliado = BaseClinica.login_afiliados(email, password)
    if not afiliado:  # Si NO existe el afiliado...
        return jsonify({"mensaje": "Afiliado NO encontrado!!"}), 409
    else:        
        session['email'] = email
        session['name'] = afiliado['nombre']
        session['surname'] = afiliado['apellido']
        
        return jsonify({"mensaje": "Afiliado encontrado!!"}), 209
#       response = make_response(render_template('prueba.html', name=session['name']))
#       return response


# --------------------------------------------------------------------
# LOGIN de USUARIOS
# --------------------------------------------------------------------
@app.route("/cons_pass_usuarios", methods=["POST"])
def login_usuarios():  # Capturo los datos que vienen del HTML
    dni = request.form["dni"]
    password = request.form["password"]

    # Me aseguro que el usuario exista
    usuario = BaseClinica.login_usuarios(dni, password)
    if not usuario:  # Si NO existe el usuario...
        return jsonify({"mensaje": "Usuario NO encontrado!!"}), 408
    else:
#        session['dni'] = dni
#        session['name'] = usuario[1]
#        session['surname'] = usuario[2]
        
        return jsonify({"mensaje": "Usuario encontrado!!"}), 208


# --------------------------------------------------------------------
# Listar todos los PUESTOS
# --------------------------------------------------------------------
@app.route(
    "/puestos", methods=["GET"]
)  # GET es el metodo para obtener respuestas a las peticiones
def listar_puestos():
    puestos = BaseClinica.listar_puestos()
    return jsonify(puestos)


# --------------------------------------------------------------------
# Listar todos los CONTRATOS
# --------------------------------------------------------------------
@app.route(
    "/contratos", methods=["GET"]
)  # GET es el metodo para obtener respuestas a las peticiones
def listar_contratos():
    contratos = BaseClinica.listar_contratos()
    return jsonify(contratos)


# --------------------------------------------------------------------
# Listar todos los ESTADOS
# --------------------------------------------------------------------
@app.route(
    "/estados", methods=["GET"]
)  # GET es el metodo para obtener respuestas a las peticiones
def listar_estados():
    estados = BaseClinica.listar_estados()
    return jsonify(estados)


# --------------------------------------------------------------------
# Agregar un MENSAJE
# --------------------------------------------------------------------
@app.route("/mensajes", methods=["POST"])
def agregar_mensaje():  # Capturo los datos que vienen del HTML
    nombre = request.form["nombre"]
    mail = request.form["mail"]
    mensaje = request.form["mensaje"]

    # Validacion de que los campos esten con datos
    if nombre == "" or mail == "" or mensaje == "":
        return (
            jsonify(
                {
                    "mensaje": "No se agrego mensaje datos faltantes",
                }
            ),
            505,
        )
    elif len(nombre) < 3 or len(mensaje) < 3:
        return (
            jsonify(
                {
                    "mensaje": "No se agrego mensaje datos faltantes",
                }
            ),
            506,
        )
    else:
        # Si esta todo validado, se agrega el mensaje a la base de datos
        if BaseClinica.agregar_mensaje(nombre, mail, mensaje):
            # Si el afiliado se agrega con éxito, se devuelve una respuesta JSON con un mensaje de éxito y un código de estado HTTP 201 (Creado).
            return (
                jsonify(
                    {
                        "mensaje": "Mensaje AGREAGADO CORRECTAMENTE!!",
                    }
                ),
                201,
            )
        else:
            # Si el producto no se puede agregar, se devuelve una respuesta JSON con un mensaje de error y un código de estado HTTP 500 (Internal Server Error).
            return (
                jsonify({"mensaje": "ERROR al agregar el MENSAJE!!"}),
                500,
            )


# *************************************  COMIENZA CRUD AFILIADOS   ****************************************************************


# --------------------------------------------------------------------
# Listar todos los afiliados
# --------------------------------------------------------------------
# Esta sentencia es la que se usa con FLASK para poder relacionar la BBDD con HTML y LISTAR TODOS los afiliados
@app.route(
    "/afiliados", methods=["GET"]
)  # GET es el metodo para obtener respuestas a las peticiones
def listar_afiliados():
    afiliados = BaseClinica.listar_afiliados()
    return jsonify(afiliados)


# --------------------------------------------------------------------
# Agregar un afiliado
# --------------------------------------------------------------------
@app.route("/afiliados", methods=["POST"])
def agregar_afiliado():  # Capturo los datos que vienen del HTML
    dni = request.form["dni"]
    nombre = request.form["nombre"]
    apellido = request.form["apellido"]
    fecha_nac = request.form["fecha_nac"]
    plan = request.form["plan"]
    foto = request.files["foto"]
    prestador = request.form["prestador"]
    nombre_imagen = ""

    # Me aseguro que el producto exista
    afiliado = BaseClinica.consultar_afiliado(dni)
    if not afiliado:  # Si no existe el afiliado...
        # Genero el nombre de la imagen
        nombre_imagen = secure_filename(
            foto.filename
        )  # Chequea el nombre del archivo de la imagen, asegurándose de que sea seguro para guardar en el sistema de archivos
        nombre_base, extension = os.path.splitext(
            nombre_imagen
        )  # Separa el nombre del archivo de su extensión.
        nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}"  # Genera un nuevo nombre para la imagen usando un timestamp, para evitar sobreescrituras y conflictos de nombres.

        # Se agrega el producto a la base de datos
        if BaseClinica.agregar_afiliado(
            dni, nombre, apellido, fecha_nac, plan, nombre_imagen, prestador
        ):
            foto.save(os.path.join(RUTA_DESTINO, nombre_imagen))

            # Si el afiliado se agrega con éxito, se devuelve una respuesta JSON con un mensaje de éxito y un código de estado HTTP 201 (Creado).
            return (
                jsonify(
                    {
                        "mensaje": "Afiliado AGREAGADO CORRECTAMENTE!!",
                        "imagen": nombre_imagen,
                    }
                ),
                201,
            )
        else:
            # Si el producto no se puede agregar, se devuelve una respuesta JSON con un mensaje de error y un código de estado HTTP 500 (Internal Server Error).
            return jsonify({"mensaje": "ERROR al agregar el afiliado!!"}), 500

    else:
        # Si el producto ya existe (basado en el código), se devuelve una respuesta JSON con un mensaje de error y un código de estado HTTP 400 (Solicitud Incorrecta).
        return jsonify({"mensaje": "EL afiliado YA EXISTE en el padron!!"}), 400


# --------------------------------------------------------------------
# Mostrar un solo afiliado según su DNI
# --------------------------------------------------------------------
# Esta sentencia es la que se usa con FLASK para poder relacionar la BBDD con HTML y CONSULTAR afiliados por DNI
@app.route("/afiliados/<int:dni>", methods=["GET"])
def consultar_afiliado(dni):
    afiliado = BaseClinica.consultar_afiliado(dni)
    if afiliado:
        return jsonify(afiliado), 201
    else:
        return "Afiliado NO ENCONTRADO!!", 404


# --------------------------------------------------------------------
# Modificar un afiliado según su DNI
# --------------------------------------------------------------------
@app.route("/afiliados/<int:dni>", methods=["PUT"])
# La ruta Flask /productos/<int:codigo> con el método HTTP PUT está diseñada para actualizar la información de un producto existente en la base de datos, identificado por su código.
# La función modificar_producto se asocia con esta URL y es invocada cuando se realiza una solicitud PUT a /productos/ seguido de un número (el código del producto).
def modificar_afiliado(dni):
    # Se recuperan los nuevos datos del formulario
    nuevo_nombre = request.form.get("nombre")
    nuevo_apellido = request.form.get("apellido")
    nueva_fecha_nac = request.form.get("fecha_nac")
    nuevo_plan = request.form.get("plan")
    nuevo_prestador = request.form.get("prestador")
    nueva_foto = request.files["foto"]

    # Procesamiento de la imagen
    nombre_imagen = secure_filename(
        nueva_foto.filename
    )  # Chequea el nombre del archivo de la imagen, asegurándose de que sea seguro para guardar en el sistema de archivos
    nombre_base, extension = os.path.splitext(
        nombre_imagen
    )  # Separa el nombre del archivo de su extensión.
    nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}"  # Genera un nuevo nombre para la imagen usando un timestamp, para evitar sobreescrituras y conflictos de nombres.

    # Busco el producto guardado
    afiliado = afiliado = BaseClinica.consultar_afiliado(dni)
    if afiliado:  # Si existe el producto...
        imagen_vieja = afiliado["foto"]
        # Armo la ruta a la imagen
        ruta_imagen = os.path.join(RUTA_DESTINO, imagen_vieja)

        # Y si existe la borro.
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)

    # Se llama al método modificar_producto pasando el codigo del producto y los nuevos datos.
    if BaseClinica.modificar_afiliado(
        dni,
        nuevo_nombre,
        nuevo_apellido,
        nueva_fecha_nac,
        nuevo_plan,
        nombre_imagen,
        nuevo_prestador,
    ):
        # La imagen se guarda en el servidor.
        nueva_foto.save(os.path.join(RUTA_DESTINO, nombre_imagen))

        # Si la actualización es exitosa, se devuelve una respuesta JSON con un mensaje de éxito y un código de estado HTTP 200 (OK).
        return jsonify({"mensaje": "Afiliado MODIFICADO EXITOSAMENTE!! 001"}), 200
    else:
        # Si el producto no se encuentra (por ejemplo, si no hay ningún producto con el código dado), se devuelve un mensaje de error con un código de estado HTTP 404 (No Encontrado).
        return jsonify({"mensaje": "Afiliado NO ENCONTRADO!! 002"}), 403


# --------------------------------------------------------------------
# Eliminar un afiliado según su DNI
# --------------------------------------------------------------------
@app.route("/afiliados/<int:dni>", methods=["DELETE"])
# La ruta Flask /productos/<int:codigo> con el método HTTP DELETE está diseñada para eliminar un producto específico de la base de datos, utilizando su código como identificador.
# La función eliminar_producto se asocia con esta URL y es llamada cuando se realiza una solicitud DELETE a /productos/ seguido de un número (el código del producto).
def eliminar_afiliado(dni):
    # Busco el producto en la base de datos
    producto = BaseClinica.consultar_afiliado(dni)
    if (
        producto
    ):  # Si el producto existe, verifica si hay una imagen asociada en el servidor.
        imagen_vieja = producto["foto"]
        # Armo la ruta a la imagen
        ruta_imagen = os.path.join(RUTA_DESTINO, imagen_vieja)

        # Y si existe, la elimina del sistema de archivos.
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)

        # Luego, elimina el producto del catálogo
        if BaseClinica.eliminar_afiliado(dni):
            # Si el producto se elimina correctamente, se devuelve una respuesta JSON con un mensaje de éxito y un código de estado HTTP 200 (OK).
            return jsonify({"mensaje": "Afiliado ELIMINADO!!"}), 200
        else:
            # Si ocurre un error durante la eliminación (por ejemplo, si el producto no se puede eliminar de la base de datos por alguna razón), se devuelve un mensaje de error con un código de estado HTTP 500 (Error Interno del Servidor).
            return jsonify({"mensaje": "ERROR al eliminar afiliado!!"}), 500
    else:
        # Si el producto no se encuentra (por ejemplo, si no existe un producto con el codigo proporcionado), se devuelve un mensaje de error con un código de estado HTTP 404 (No Encontrado).
        return jsonify({"mensaje": "Afiliado NO ENCONTRADO!!"}), 404


# ************************************   FIN FASE CRUD AFILIADOS   **************************************************************


# *************************************  COMIENZA CRUD EMPRESAS   ****************************************************************

# --------------------------------------------------------------------
# Agregar una empresa
# --------------------------------------------------------------------


@app.route("/empresas", methods=["POST"])
def agregar_empresa():  # Capturo los datos que vienen del HTML
    codigo = request.form["codigo"]
    nombre = request.form["nombre"]
    rubro = request.form["rubro"]
    direccion = request.form["direccion"]
    mail = request.form["mail"]

    # Me aseguro que la empresa exista
    empresa = BaseClinica.consultar_empresa(codigo)
    if not empresa:  # Si no existe el afiliado...
        # Se agrega la empresa a la base de datos
        if BaseClinica.agregar_empresa(codigo, nombre, rubro, direccion, mail):
            # Si la empresa se agrega con éxito, se devuelve una respuesta JSON con un mensaje de éxito y un código de estado HTTP 201 (Creado).
            return (
                jsonify(
                    {
                        "mensaje": "Empresa AGREAGADA CORRECTAMENTE!!",
                    }
                ),
                201,
            )
        else:
            # Si la empresa no se puede agregar, se devuelve una respuesta JSON con un mensaje de error y un código de estado HTTP 500 (Internal Server Error).
            return (
                jsonify({"mensaje": "ERROR al agregar la empresa!!"}),
                500,
            )
    else:
        # Si la empresa ya existe (basado en el código), se devuelve una respuesta JSON con un mensaje de error y un código de estado HTTP 400 (Solicitud Incorrecta).
        return (
            jsonify(
                {
                    "mensaje": "Empresa ya existente!!",
                }
            ),
            400,
        )


# --------------------------------------------------------------------
# Listar todas las empresas
# --------------------------------------------------------------------
# Esta sentencia es la que se usa con FLASK para poder relacionar la BBDD con HTML y LISTAR TODAS las empresas
@app.route(
    "/empresas", methods=["GET"]
)  # GET es el metodo para obtener respuestas a las peticiones
def listar_empresas():
    empresas = BaseClinica.listar_empresas()
    return jsonify(empresas)


# --------------------------------------------------------------------
# Modificar una empresa por su codigo
# --------------------------------------------------------------------
@app.route("/empresas/<int:codigo>", methods=["PUT"])
# La ruta Flask /empresas/<int:codigo> con el método HTTP PUT está diseñada para actualizar la información de una empresa existente en la base de datos, identificado por su código.
# La función modificar_empresa se asocia con esta URL y es invocada cuando se realiza una solicitud PUT a /empresas/ seguido del codigo.
def modificar_empresa(codigo):
    # Se recuperan los nuevos datos del formulario
    nuevo_nombre = request.form.get("nombre")
    nuevo_rubro = request.form.get("rubro")
    nueva_direccion = request.form.get("direccion")
    nuevo_mail = request.form.get("mail")

    # Busco la empresa guardada
    empresa = empresa = BaseClinica.consultar_empresa(codigo)

    """
    if empresa:  # Si existe el producto...
        imagen_vieja = empresa["foto"]
        # Armo la ruta a la imagen
        ruta_imagen = os.path.join(RUTA_DESTINO, imagen_vieja)

        # Y si existe la borro.
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)
    """

    # Se llama al método modificar_empresa pasando el codigo de la empresa y los nuevos datos.
    if BaseClinica.modificar_empresa(
        codigo,
        nuevo_nombre,
        nuevo_rubro,
        nueva_direccion,
        nuevo_mail,
    ):
        # La imagen se guarda en el servidor.
        # nueva_foto.save(os.path.join(RUTA_DESTINO, nombre_imagen))

        # Si la actualización es exitosa, se devuelve una respuesta JSON con un mensaje de éxito y un código de estado HTTP 200 (OK).
        return jsonify({"mensaje": "Empresa MODIFICADA EXITOSAMENTE!! 001"}), 200
    else:
        # Si el producto no se encuentra (por ejemplo, si no hay ningún producto con el código dado), se devuelve un mensaje de error con un código de estado HTTP 404 (No Encontrado).
        return jsonify({"mensaje": "Empresa NO ENCONTRADA!! 002"}), 403


# --------------------------------------------------------------------
# Mostrar una empresa por su codigo
# --------------------------------------------------------------------
# Esta sentencia es la que se usa con FLASK para poder relacionar la BBDD con HTML y CONSULTAR empresa por codigo
@app.route("/empresas/<int:codigo>", methods=["GET"])
def consultar_empresa(codigo):
    empresa = BaseClinica.consultar_empresa(codigo)
    if empresa:
        return jsonify(empresa), 201
    else:
        return "Empresa NO ENCONTRADA!", 404


# --------------------------------------------------------------------
# Eliminar una empresa segun su codigo
# --------------------------------------------------------------------
@app.route("/empresas/<int:codigo>", methods=["DELETE"])
# La ruta Flask /empresas/<int:codigo> con el método HTTP DELETE está diseñada para eliminar un producto específico de la base de datos, utilizando su código como identificador.
# La función eliminar_empresa se asocia con esta URL y es llamada cuando se realiza una solicitud DELETE a /empresas/ seguido de codigo
def eliminar_empresa(codigo):
    # Busco la empresa en la base de datos
    empresa = BaseClinica.consultar_empresa(codigo)
    if (
        codigo
    ):  # Si la empresa existe, verifica si hay una imagen asociada en el servidor.
        # Luego, elimina la empresa del catálogo
        if BaseClinica.eliminar_empresa(codigo):
            # Si la empresa se elimina correctamente, se devuelve una respuesta JSON con un mensaje de éxito y un código de estado HTTP 200 (OK).
            return jsonify({"mensaje": "Empresa ELIMINADO!!"}), 200
        else:
            # Si ocurre un error durante la eliminación (por ejemplo, si la empresa no se puede eliminar de la base de datos por alguna razón), se devuelve un mensaje de error con un código de estado HTTP 500 (Error Interno del Servidor).
            return jsonify({"mensaje": "ERROR al eliminar empresa!!"}), 500
    else:
        # Si la empresa no se encuentra (por ejemplo, si no existe con el codigo proporcionado), se devuelve un mensaje de error con un código de estado HTTP 404 (No Encontrado).
        return jsonify({"mensaje": "Empresa NO ENCONTRADO!!"}), 404


# ************************************   FIN FASE CRUD EMPRESAS   **************************************************************


# *************************************  COMIENZA CRUD USUARIOS   *************************************************************
# --------------------------------------------------------------------
# Agregar un usuario
# --------------------------------------------------------------------
@app.route("/usuarios", methods=["POST"])
def agregar_usuario():  # Capturo los datos que vienen del HTML
    dni = request.form["dni"]
    nombre = request.form["nombre"]
    apellido = request.form["apellido"]
    fecha_nac = request.form["fecha_nac"]
    puesto = request.form["puesto"]
    contrato = request.form["contrato"]
    foto = request.files["foto"]
    password = request.form["password"]
    empresa = request.form["empresa"]
    estado = request.form["estado"]
    nombre_imagen = ""

    # Me aseguro que el usuario exista
    usuario = BaseClinica.consultar_usuario(dni)
    if not usuario:  # Si no existe el usuario...
        # Genero el nombre de la imagen
        nombre_imagen = secure_filename(
            foto.filename
        )  # Chequea el nombre del archivo de la imagen, asegurándose de que sea seguro para guardar en el sistema de archivos
        nombre_base, extension = os.path.splitext(
            nombre_imagen
        )  # Separa el nombre del archivo de su extensión.
        nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}"  # Genera un nuevo nombre para la imagen usando un timestamp, para evitar sobreescrituras y conflictos de nombres.

        # Se agrega el usuario a la base de datos y su foto al repositorio de imagenes
        if BaseClinica.agregar_usuario(
            dni,
            nombre,
            apellido,
            fecha_nac,
            puesto,
            contrato,
            nombre_imagen,
            password,
            empresa,
            estado,
        ):
            foto.save(os.path.join(RUTA_DESTINO, nombre_imagen))

            # Si el usuario se agrega con éxito, se devuelve una respuesta JSON con un mensaje de éxito y un código de estado HTTP 201 (Creado).
            return (
                jsonify(
                    {
                        "mensaje": "Usuario AGREAGADO CORRECTAMENTE!!",
                        "imagen": nombre_imagen,
                    }
                ),
                201,
            )
        else:
            # Si el usuario no se puede agregar, se devuelve una respuesta JSON con un mensaje de error y un código de estado HTTP 500 (Internal Server Error).
            return jsonify({"mensaje": "ERROR al agregar el usuario!!"}), 500

    else:
        # Si el usuario ya existe (basado en el DNI), se devuelve una respuesta JSON con un mensaje de error y un código de estado HTTP 400 (Solicitud Incorrecta).
        return jsonify({"mensaje": "EL usuario YA EXISTE en la nómina!!"}), 400


# --------------------------------------------------------------------
# Modificar un usuario según su DNI
# --------------------------------------------------------------------
@app.route("/usuarios/<int:dni>", methods=["PUT"])
# La ruta Flask /productos/<int:codigo> con el método HTTP PUT está diseñada para actualizar la información de un producto existente en la base de datos, identificado por su código.
# La función modificar_producto se asocia con esta URL y es invocada cuando se realiza una solicitud PUT a /productos/ seguido de un número (el código del producto).
def modificar_usuario(dni):
    # Se recuperan los nuevos datos del formulario
    nuevo_nombre = request.form.get("nombre")
    nuevo_apellido = request.form.get("apellido")
    nueva_fecha_nac = request.form.get("fecha_nac")
    nuevo_puesto = request.form.get("puesto")
    nuevo_contrato = request.form.get("contrato")
    nueva_empresa = request.form.get("empresa")
    nuevo_estado = request.form.get("estado")
    nueva_foto = request.files["foto"]

    # Procesamiento de la imagen
    nombre_imagen = secure_filename(
        nueva_foto.filename
    )  # Chequea el nombre del archivo de la imagen, asegurándose de que sea seguro para guardar en el sistema de archivos
    nombre_base, extension = os.path.splitext(
        nombre_imagen
    )  # Separa el nombre del archivo de su extensión.
    nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}"  # Genera un nuevo nombre para la imagen usando un timestamp, para evitar sobreescrituras y conflictos de nombres.

    # Busco el producto guardado
    usuario = usuario = BaseClinica.consultar_usuario(dni)
    if usuario:  # Si existe el producto...
        imagen_vieja = usuario["foto"]
        # Armo la ruta a la imagen
        ruta_imagen = os.path.join(RUTA_DESTINO, imagen_vieja)

        # Y si existe la borro.
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)

    # Se llama al método modificar_producto pasando el codigo del producto y los nuevos datos.
    if BaseClinica.modificar_usuario(
        dni,
        nuevo_nombre,
        nuevo_apellido,
        nueva_fecha_nac,
        nuevo_puesto,
        nuevo_contrato,
        nombre_imagen,
        nueva_empresa,
        nuevo_estado,
    ):
        # La imagen se guarda en el servidor.
        nueva_foto.save(os.path.join(RUTA_DESTINO, nombre_imagen))

        # Si la actualización es exitosa, se devuelve una respuesta JSON con un mensaje de éxito y un código de estado HTTP 200 (OK).
        return jsonify({"mensaje": "Afiliado MODIFICADO EXITOSAMENTE!! 001"}), 200
    else:
        # Si el producto no se encuentra (por ejemplo, si no hay ningún producto con el código dado), se devuelve un mensaje de error con un código de estado HTTP 404 (No Encontrado).
        return jsonify({"mensaje": "Afiliado NO ENCONTRADO!! 002"}), 403


# --------------------------------------------------------------------
# Listar todos los usuarios - Listado generado por VISTA en BBDD
# --------------------------------------------------------------------
# Esta sentencia es la que se usa con FLASK para poder relacionar la BBDD con HTML y LISTAR TODOS los usuarios
@app.route(
    "/cons_usuarios", methods=["GET"]
)  # GET es el metodo para obtener respuestas a las peticiones
def listar_usuarios():
    usuarios = BaseClinica.listar_usuarios()
    return jsonify(usuarios)


# --------------------------------------------------------------------
# Listar todos los usuarios - Listado generado por TABLA USUARIOS - PARA LISTADO ELIMINAR USUARIOS
# --------------------------------------------------------------------
# Esta sentencia es la que se usa con FLASK para poder relacionar la BBDD con HTML y LISTAR TODOS los usuarios
@app.route(
    "/usuarios", methods=["GET"]
)  # GET es el metodo para obtener respuestas a las peticiones
def listar_usuarios_crudo():
    usuarios = BaseClinica.listar_usuarios_crudo()
    return jsonify(usuarios)


# --------------------------------------------------------------------
# Mostrar un solo usuario según su DNI
# --------------------------------------------------------------------
# Esta sentencia es la que se usa con FLASK para poder relacionar la BBDD con HTML y CONSULTAR usuario por DNI
@app.route("/usuarios/<int:dni>", methods=["GET"])
def consultar_usuario(dni):
    usuario = BaseClinica.consultar_usuario(dni)
    if usuario:
        return jsonify(usuario), 201
    else:
        return "Usuario NO ENCONTRADO!!", 404


# --------------------------------------------------------------------
# Eliminar un usuario según su DNI
# --------------------------------------------------------------------
@app.route("/usuarios/<int:dni>", methods=["DELETE"])
# La ruta Flask /usuarios/<int:dni> con el método HTTP DELETE está diseñada para eliminar un usuario específico de la base de datos, utilizando su DNI como identificador.
# La función eliminar_usuario se asocia con esta URL y es llamada cuando se realiza una solicitud DELETE a /uaurios/ seguido de un número (el DNI del usuario).
def eliminar_usuario(dni):
    # Busco el usuario en la base de datos
    usuario = BaseClinica.consultar_usuario(dni)
    if (
        usuario
    ):  # Si el usuario existe, verifica si hay una imagen asociada en el servidor.
        imagen_vieja = usuario["foto"]
        # Armo la ruta a la imagen
        ruta_imagen = os.path.join(RUTA_DESTINO, imagen_vieja)

        # Y si existe, la elimina del sistema de archivos.
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)

        # Luego, elimina el usuario del catálogo
        if BaseClinica.eliminar_usuario(dni):
            # Si el usuario se elimina correctamente, se devuelve una respuesta JSON con un mensaje de éxito y un código de estado HTTP 200 (OK).
            return jsonify({"mensaje": "Usuario ELIMINADO correctamente!!"}), 200
        else:
            # Si ocurre un error durante la eliminación (por ejemplo, si el usuario no se puede eliminar de la base de datos por alguna razón), se devuelve un mensaje de error con un código de estado HTTP 500 (Error Interno del Servidor).
            return jsonify({"mensaje": "ERROR al eliminar usuario!!"}), 500
    else:
        # Si el usuario no se encuentra (por ejemplo, si no existe un usuario con el DNI proporcionado), se devuelve un mensaje de error con un código de estado HTTP 404 (No Encontrado).
        return jsonify({"mensaje": "Usuario NO ENCONTRADO en nómina!!"}), 404


# --------------------------------------------------------------------------------------------------------------------------
# Esto es para levantar el servicio y se pueda ejecutar
if __name__ == "__main__":
    app.run(debug=True)
