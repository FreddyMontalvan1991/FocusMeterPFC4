from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

base = "FocusMeter"

dias_es = {
        0: "Lunes",
        1: "Martes",
        2: "Miércoles",
        3: "Jueves",
        4: "Viernes",
        5: "Sábado",
        6: "Domingo"
    }

def get_cliente_mongo():
    uri = (
        "mongodb+srv://Adrian_bd:Administrador31.@base.f1r4j33.mongodb.net/"
        "FocusMeter?retryWrites=true&w=majority&appName=Base"
    )
    return MongoClient(uri)


def insertar_registro_atencion(registro):
    

    cliente = get_cliente_mongo()
    coleccion = cliente[base]["registros_atencion"]

    documento = {
        "num_estudiantes_detectados": registro.num_estudiantes_detectados,
        "porcentaje_estimado_atencion": registro.porcentaje_estimado_atencion,
        "porcentajes_etiquetas": registro.porcentajes_etiquetas,
        "num_deteccion_etiquetas": registro.num_deteccion_etiquetas,
        "fecha_deteccion": registro.fecha_deteccion,
        "hora_detecccion": registro.hora_detecccion,
        "id_horario": registro.id_horario
    }

    return coleccion.insert_one(documento)


def obtener_horario_actual(id_aula):

    ahora = datetime.now()
    dia = dias_es[ahora.weekday()]
    hora_actual = ahora.strftime("%H:00")

    cliente = get_cliente_mongo()
    coleccion = cliente[base]["horarios"]

    horario = coleccion.find_one({
        "id_aula": id_aula,
        "dia": dia,
        "hora_inicio": hora_actual
    })

    if horario:
        coleccion = cliente[base]["asignaturas"]
        asignatura = coleccion.find_one({
            "_id": ObjectId(horario['id_asignatura'])
        })

        coleccion = cliente[base]["docentes"]
        docente = coleccion.find_one({
            "_id": ObjectId(asignatura['id_docente'])
        })

        coleccion = cliente[base]["carreras"]
        carrera = coleccion.find_one({
            "_id": ObjectId(asignatura['id_carrera'])
        })

        return {
            "asignatura": asignatura["nombre_asignatura"],
            "docente": docente["nombre"],
            "carrera": carrera["nombre_carrera"],
            "ciclo": asignatura["num_ciclo"],
            "Hora_inicio": horario["hora_inicio"],
            "hora_fin": horario["hora_fin"],
            "periodo_academico": asignatura["periodo_academico"]
        }
    
    return None

    





def obtener_asignatura_horario(id_asignatura):
    pass