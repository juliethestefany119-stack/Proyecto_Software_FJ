# =============================================================
# PROYECTO: SISTEMA INTEGRAL DE GESTION SOFTWARE FJ
# CURSO: PROGRAMACION - 213023
# FASE 4 - COMPONENTE PRACTICO
# =============================================================

from abc import ABC, abstractmethod
from datetime import datetime
import logging


# =============================================================
# CONFIGURACION DEL SISTEMA DE REGISTROS (LOGS)
# =============================================================

logging.basicConfig(
    filename="software_fj.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8"
)

logger = logging.getLogger("SoftwareFJ")


# =============================================================
# EXCEPCIONES PERSONALIZADAS
# =============================================================

class AplicacionError(Exception):
    """Excepcion base del sistema."""
    pass


class ValidacionError(AplicacionError):
    """Error cuando los datos no cumplen las validaciones."""
    pass


class RecursoNoDisponibleError(AplicacionError):
    """Error cuando un servicio no esta disponible."""
    pass


class ReservaNoEncontradaError(AplicacionError):
    """Error cuando no existe una reserva."""
    pass


class EstadoReservaError(AplicacionError):
    """Error cuando una operacion no corresponde al estado."""
    pass


# =============================================================
# CLASE ABSTRACTA ENTIDAD
# =============================================================

class Entidad(ABC):

    def __init__(self, identificador):

        if identificador is None or str(identificador).strip() == "":
            raise ValidacionError(
                "El identificador es obligatorio."
            )

        self._identificador = str(identificador).strip()

    @property
    def identificador(self):
        return self._identificador

    @abstractmethod
    def mostrar_informacion(self):
        pass


# =============================================================
# CLASE CLIENTE
# =============================================================

class Cliente(Entidad):

    def __init__(self, identificador, nombre, correo, telefono):

        super().__init__(identificador)

        self.__nombre = self.validar_nombre(nombre)
        self.__correo = self.validar_correo(correo)
        self.__telefono = self.validar_telefono(telefono)

    @staticmethod
    def validar_nombre(nombre):

        if not isinstance(nombre, str) or len(nombre.strip()) < 2:
            raise ValidacionError(
                "El nombre debe tener al menos 2 caracteres."
            )

        return nombre.strip()

    @staticmethod
    def validar_correo(correo):

        if not isinstance(correo, str):
            raise ValidacionError("El correo debe ser un texto.")

        correo = correo.strip().lower()

        if "@" not in correo or "." not in correo.split("@")[-1]:
            raise ValidacionError(
                "El correo electronico no es valido."
            )

        return correo

    @staticmethod
    def validar_telefono(telefono):

        numero = str(telefono).replace(" ", "").replace("-", "")

        if not numero.isdigit():
            raise ValidacionError(
                "El telefono debe contener solamente numeros."
            )

        if len(numero) < 7 or len(numero) > 15:
            raise ValidacionError(
                "El telefono debe tener entre 7 y 15 digitos."
            )

        return numero

    @property
    def nombre(self):
        return self.__nombre

    @property
    def correo(self):
        return self.__correo

    @property
    def telefono(self):
        return self.__telefono

    def mostrar_informacion(self):

        return (
            f"Cliente: {self.nombre} | "
            f"Identificacion: {self.identificador} | "
            f"Correo: {self.correo} | "
            f"Telefono: {self.telefono}"
        )


# =============================================================
# CLASE ABSTRACTA SERVICIO
# =============================================================

class Servicio(Entidad):

    def __init__(
        self,
        identificador,
        nombre,
        tarifa_base,
        disponible=True
    ):

        super().__init__(identificador)

        if not isinstance(nombre, str) or len(nombre.strip()) < 3:
            raise ValidacionError(
                "El nombre del servicio debe tener al menos 3 caracteres."
            )

        if (
            isinstance(tarifa_base, bool)
            or not isinstance(tarifa_base, (int, float))
            or tarifa_base <= 0
        ):
            raise ValidacionError(
                "La tarifa base debe ser mayor que cero."
            )

        if not isinstance(disponible, bool):
            raise ValidacionError(
                "La disponibilidad debe ser True o False."
            )

        self._nombre = nombre.strip()
        self._tarifa_base = float(tarifa_base)
        self._disponible = disponible

    @property
    def nombre(self):
        return self._nombre

    @property
    def tarifa_base(self):
        return self._tarifa_base

    @property
    def disponible(self):
        return self._disponible

    def cambiar_disponibilidad(self, estado):

        if not isinstance(estado, bool):
            raise ValidacionError(
                "El estado debe ser True o False."
            )

        self._disponible = estado

        logger.info(
            "Disponibilidad del servicio %s modificada a %s",
            self.identificador,
            estado
        )

    def validar_disponibilidad(self):

        if not self._disponible:
            raise RecursoNoDisponibleError(
                f"El servicio {self.nombre} no esta disponible."
            )

    @abstractmethod
    def calcular_costo(self, cantidad=1, descuento=0):
        pass

    @abstractmethod
    def describir(self):
        pass

    def mostrar_informacion(self):
        return self.describir()


# =============================================================
# SERVICIO ESPECIALIZADO 1: RESERVA DE SALAS
# =============================================================

class ReservaSala(Servicio):

    def __init__(
        self,
        identificador,
        nombre,
        tarifa_base,
        capacidad,
        disponible=True
    ):

        super().__init__(
            identificador,
            nombre,
            tarifa_base,
            disponible
        )

        if not isinstance(capacidad, int) or capacidad <= 0:
            raise ValidacionError(
                "La capacidad debe ser un entero mayor que cero."
            )

        self.capacidad = capacidad

    def calcular_costo(self, cantidad=1, descuento=0):

        self.validar_disponibilidad()

        if cantidad <= 0:
            raise ValidacionError(
                "La cantidad de horas debe ser mayor que cero."
            )

        if descuento < 0 or descuento > 100:
            raise ValidacionError(
                "El descuento debe estar entre 0 y 100."
            )

        subtotal = self.tarifa_base * cantidad

        return subtotal - (subtotal * descuento / 100)

    def describir(self):

        return (
            f"Sala: {self.nombre} | "
            f"Tarifa por hora: ${self.tarifa_base:,.2f} | "
            f"Capacidad: {self.capacidad} personas | "
            f"Disponible: {self.disponible}"
        )


# =============================================================
# SERVICIO ESPECIALIZADO 2: ALQUILER DE EQUIPOS
# =============================================================

class AlquilerEquipo(Servicio):

    def __init__(
        self,
        identificador,
        nombre,
        tarifa_base,
        cantidad_disponible,
        disponible=True
    ):

        super().__init__(
            identificador,
            nombre,
            tarifa_base,
            disponible
        )

        if (
            not isinstance(cantidad_disponible, int)
            or cantidad_disponible < 0
        ):
            raise ValidacionError(
                "La cantidad de equipos no puede ser negativa."
            )

        self.cantidad_disponible = cantidad_disponible

    def calcular_costo(self, cantidad=1, descuento=0, dias=1):

        self.validar_disponibilidad()

        if cantidad <= 0:
            raise ValidacionError(
                "La cantidad de equipos debe ser mayor que cero."
            )

        if dias <= 0:
            raise ValidacionError(
                "Los dias de alquiler deben ser mayores que cero."
            )

        if cantidad > self.cantidad_disponible:
            raise RecursoNoDisponibleError(
                "No hay suficientes equipos disponibles."
            )

        if descuento < 0 or descuento > 100:
            raise ValidacionError(
                "El descuento debe estar entre 0 y 100."
            )

        subtotal = self.tarifa_base * cantidad * dias

        return subtotal - (subtotal * descuento / 100)

    def describir(self):

        return (
            f"Equipo: {self.nombre} | "
            f"Tarifa diaria: ${self.tarifa_base:,.2f} | "
            f"Cantidad disponible: {self.cantidad_disponible} | "
            f"Disponible: {self.disponible}"
        )


# =============================================================
# SERVICIO ESPECIALIZADO 3: ASESORIAS ESPECIALIZADAS
# =============================================================

class AsesoriaEspecializada(Servicio):

    def __init__(
        self,
        identificador,
        nombre,
        tarifa_base,
        especialidad,
        disponible=True
    ):

        super().__init__(
            identificador,
            nombre,
            tarifa_base,
            disponible
        )

        if not isinstance(especialidad, str) or len(especialidad.strip()) < 3:
            raise ValidacionError(
                "La especialidad debe tener al menos 3 caracteres."
            )

        self.especialidad = especialidad.strip()

    def calcular_costo(self, cantidad=1, descuento=0):

        self.validar_disponibilidad()

        if cantidad <= 0:
            raise ValidacionError(
                "Las horas de asesoria deben ser mayores que cero."
            )

        if descuento < 0 or descuento > 100:
            raise ValidacionError(
                "El descuento debe estar entre 0 y 100."
            )

        subtotal = self.tarifa_base * cantidad

        return subtotal - (subtotal * descuento / 100)

    def describir(self):

        return (
            f"Asesoria: {self.nombre} | "
            f"Especialidad: {self.especialidad} | "
            f"Tarifa por hora: ${self.tarifa_base:,.2f} | "
            f"Disponible: {self.disponible}"
        )


# =============================================================
# CLASE RESERVA
# =============================================================

class Reserva(Entidad):

    ESTADOS_VALIDOS = [
        "PENDIENTE",
        "CONFIRMADA",
        "CANCELADA",
        "PROCESADA"
    ]

    def __init__(
        self,
        identificador,
        cliente,
        servicio,
        duracion,
        observaciones=""
    ):

        super().__init__(identificador)

        if not isinstance(cliente, Cliente):
            raise ValidacionError(
                "Debe proporcionar un cliente valido."
            )

        if not isinstance(servicio, Servicio):
            raise ValidacionError(
                "Debe proporcionar un servicio valido."
            )

        if (
            isinstance(duracion, bool)
            or not isinstance(duracion, (int, float))
            or duracion <= 0
        ):
            raise ValidacionError(
                "La duracion debe ser mayor que cero."
            )

        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.observaciones = observaciones
        self.estado = "PENDIENTE"
        self.fecha_creacion = datetime.now()
        self.costo = 0

    def confirmar(self):

        if self.estado != "PENDIENTE":
            raise EstadoReservaError(
                "Solamente se pueden confirmar reservas pendientes."
            )

        self.servicio.validar_disponibilidad()

        self.estado = "CONFIRMADA"

        logger.info(
            "Reserva %s confirmada.",
            self.identificador
        )

        return "Reserva confirmada correctamente."

    def cancelar(self):

        if self.estado not in ["PENDIENTE", "CONFIRMADA"]:
            raise EstadoReservaError(
                "No se puede cancelar una reserva procesada o cancelada."
            )

        self.estado = "CANCELADA"

        logger.info(
            "Reserva %s cancelada.",
            self.identificador
        )

        return "Reserva cancelada correctamente."

    def procesar(self, descuento=0):

        if self.estado != "CONFIRMADA":
            raise EstadoReservaError(
                "La reserva debe estar confirmada para procesarse."
            )

        self.servicio.validar_disponibilidad()

        # Polimorfismo: cada servicio calcula el costo
        # de acuerdo con su propia implementacion.
        self.costo = self.servicio.calcular_costo(
            self.duracion,
            descuento
        )

        self.estado = "PROCESADA"

        logger.info(
            "Reserva %s procesada. Costo: %.2f",
            self.identificador,
            self.costo
        )

        return self.costo

    def mostrar_informacion(self):

        return (
            f"Reserva: {self.identificador}\n"
            f"Cliente: {self.cliente.nombre}\n"
            f"Servicio: {self.servicio.nombre}\n"
            f"Duracion: {self.duracion}\n"
            f"Estado: {self.estado}\n"
            f"Costo: ${self.costo:,.2f}"
        )


# =============================================================
# CLASE PRINCIPAL DEL SISTEMA
# =============================================================

class SistemaSoftwareFJ:

    def __init__(self):

        self.clientes = []
        self.servicios = []
        self.reservas = []

    # ---------------------------------------------------------
    # REGISTRAR CLIENTE
    # ---------------------------------------------------------

    def registrar_cliente(
        self,
        identificador,
        nombre,
        correo,
        telefono
    ):

        try:

            if any(
                c.identificador == identificador
                for c in self.clientes
            ):
                raise ValidacionError(
                    "Ya existe un cliente con ese identificador."
                )

            cliente = Cliente(
                identificador,
                nombre,
                correo,
                telefono
            )

            self.clientes.append(cliente)

        except ValidacionError as error:

            logger.error(
                "Error al registrar cliente: %s",
                error
            )

            raise

        else:

            logger.info(
                "Cliente %s registrado correctamente.",
                identificador
            )

            return cliente

        finally:

            logger.info(
                "Finalizo la operacion de registro de cliente."
            )

    # ---------------------------------------------------------
    # REGISTRAR SERVICIO
    # ---------------------------------------------------------

    def registrar_servicio(self, servicio):

        if not isinstance(servicio, Servicio):
            raise ValidacionError(
                "El objeto proporcionado no es un servicio valido."
            )

        if any(
            s.identificador == servicio.identificador
            for s in self.servicios
        ):
            raise ValidacionError(
                "Ya existe un servicio con ese identificador."
            )

        self.servicios.append(servicio)

        logger.info(
            "Servicio %s registrado correctamente.",
            servicio.identificador
        )

        return servicio

    # ---------------------------------------------------------
    # BUSCAR CLIENTE
    # ---------------------------------------------------------

    def buscar_cliente(self, identificador):

        for cliente in self.clientes:

            if cliente.identificador == identificador:
                return cliente

        raise ValidacionError(
            f"No se encontro el cliente {identificador}."
        )

    # ---------------------------------------------------------
    # BUSCAR SERVICIO
    # ---------------------------------------------------------

    def buscar_servicio(self, identificador):

        for servicio in self.servicios:

            if servicio.identificador == identificador:
                return servicio

        raise ValidacionError(
            f"No se encontro el servicio {identificador}."
        )

    # ---------------------------------------------------------
    # CREAR RESERVA
    # ---------------------------------------------------------

    def crear_reserva(
        self,
        identificador,
        cliente_id,
        servicio_id,
        duracion,
        observaciones=""
    ):

        try:

            if any(
                r.identificador == identificador
                for r in self.reservas
            ):
                raise ValidacionError(
                    "Ya existe una reserva con ese identificador."
                )

            cliente = self.buscar_cliente(cliente_id)
            servicio = self.buscar_servicio(servicio_id)

            servicio.validar_disponibilidad()

            reserva = Reserva(
                identificador,
                cliente,
                servicio,
                duracion,
                observaciones
            )

            self.reservas.append(reserva)

        except ValidacionError:
            raise

        except AplicacionError:
            raise

        except Exception as error:

            raise AplicacionError(
                "Ocurrio un error inesperado al crear la reserva."
            ) from error

        else:

            logger.info(
                "Reserva %s creada correctamente.",
                identificador
            )

            return reserva

        finally:

            logger.info(
                "Finalizo la operacion de creacion de reserva."
            )

    # ---------------------------------------------------------
    # BUSCAR RESERVAS
    # ---------------------------------------------------------

    def buscar_reservas(self, cliente_id=None, estado=None):
        """
        Metodo con parametros opcionales.
        Permite buscar todas las reservas o filtrar
        por cliente, estado o ambos.
        """

        resultados = self.reservas

        if cliente_id is not None:

            resultados = [
                r for r in resultados
                if r.cliente.identificador == cliente_id
            ]

        if estado is not None:

            resultados = [
                r for r in resultados
                if r.estado == estado.upper()
            ]

        return resultados

    # ---------------------------------------------------------
    # OBTENER RESERVA
    # ---------------------------------------------------------

    def obtener_reserva(self, identificador):

        for reserva in self.reservas:

            if reserva.identificador == identificador:
                return reserva

        raise ReservaNoEncontradaError(
            f"No se encontro la reserva {identificador}."
        )

    # ---------------------------------------------------------
    # LISTAR CLIENTES
    # ---------------------------------------------------------

    def listar_clientes(self):

        for cliente in self.clientes:
            print(cliente.mostrar_informacion())

    # ---------------------------------------------------------
    # LISTAR SERVICIOS
    # ---------------------------------------------------------

    def listar_servicios(self):

        for servicio in self.servicios:
            print(servicio.mostrar_informacion())

    # ---------------------------------------------------------
    # LISTAR RESERVAS
    # ---------------------------------------------------------

    def listar_reservas(self):

        for reserva in self.reservas:
            print(reserva.mostrar_informacion())
            print("-" * 50)


# =============================================================
# FUNCION PARA EJECUTAR OPERACIONES Y CAPTURAR EXCEPCIONES
# =============================================================

def ejecutar_operacion(nombre, funcion):

    print(f"\nOPERACION: {nombre}")

    try:

        resultado = funcion()

    except AplicacionError as error:

        print(f"ERROR CONTROLADO: {error}")

        logger.error(
            "Operacion '%s' fallida: %s",
            nombre,
            error
        )

    except Exception as error:

        print(f"ERROR INESPERADO: {error}")

        logger.exception(
            "Error inesperado en la operacion '%s'.",
            nombre
        )

    else:

        print("RESULTADO:", resultado)

        logger.info(
            "Operacion '%s' ejecutada correctamente.",
            nombre
        )

    finally:

        print("Finalizacion de la operacion:", nombre)


# =============================================================
# FUNCION PRINCIPAL: SIMULACION DEL SISTEMA
# =============================================================

def ejecutar_sistema():

    print("\n")
    print("=" * 65)
    print(" SISTEMA INTEGRAL DE GESTION DE CLIENTES, SERVICIOS Y RESERVAS")
    print(" SOFTWARE FJ")
    print("=" * 65)

    sistema = SistemaSoftwareFJ()

    # ---------------------------------------------------------
    # REGISTRO DE SERVICIOS
    # ---------------------------------------------------------

    sala = ReservaSala(
        "S001",
        "Sala de reuniones",
        50000,
        20
    )

    equipo = AlquilerEquipo(
        "E001",
        "Computador portatil",
        30000,
        10
    )

    asesoria = AsesoriaEspecializada(
        "A001",
        "Asesoria en desarrollo de software",
        80000,
        "Desarrollo de software"
    )

    sistema.registrar_servicio(sala)
    sistema.registrar_servicio(equipo)
    sistema.registrar_servicio(asesoria)

    print("\nSERVICIOS REGISTRADOS:")
    sistema.listar_servicios()

    # ---------------------------------------------------------
    # SIMULACIONES
    # ---------------------------------------------------------

    print("\n")
    print("=" * 65)
    print("SIMULACION DE OPERACIONES VALIDAS E INVALIDAS")
    print("=" * 65)

    # OPERACION 1: REGISTRO CORRECTO DE CLIENTE.

    ejecutar_operacion(
        "1. Registrar cliente valido",
        lambda: sistema.registrar_cliente(
            "C001",
            "Laura Gomez",
            "laura@gmail.com",
            "3001234567"
        ).mostrar_informacion()
    )

    # OPERACION 2: REGISTRO DE OTRO CLIENTE.

    ejecutar_operacion(
        "2. Registrar segundo cliente",
        lambda: sistema.registrar_cliente(
            "C002",
            "Carlos Perez",
            "carlos@gmail.com",
            "3107654321"
        ).mostrar_informacion()
    )

    # OPERACION 3: REGISTRO DE CLIENTE CON CORREO INVALIDO.

    ejecutar_operacion(
        "3. Registrar cliente con correo incorrecto",
        lambda: sistema.registrar_cliente(
            "C003",
            "Maria Lopez",
            "correo_incorrecto",
            "3201234567"
        )
    )

    # OPERACION 4: REGISTRO DE CLIENTE CON TELEFONO INVALIDO.

    ejecutar_operacion(
        "4. Registrar cliente con telefono incorrecto",
        lambda: sistema.registrar_cliente(
            "C004",
            "Pedro Ramirez",
            "pedro@gmail.com",
            "ABC123"
        )
    )

    # OPERACION 5: CREAR RESERVA DE SALA.

    ejecutar_operacion(
        "5. Crear reserva de sala",
        lambda: sistema.crear_reserva(
            "R001",
            "C001",
            "S001",
            2,
            "Reunion empresarial"
        ).mostrar_informacion()
    )

    # OPERACION 6: CONFIRMAR RESERVA.

    ejecutar_operacion(
        "6. Confirmar reserva",
        lambda: sistema.obtener_reserva("R001").confirmar()
    )

    # OPERACION 7: PROCESAR RESERVA.

    ejecutar_operacion(
        "7. Procesar reserva",
        lambda: (
            f"Costo de la reserva: "
            f"${sistema.obtener_reserva('R001').procesar():,.2f}"
        )
    )

    # OPERACION 8: INTENTAR CANCELAR RESERVA PROCESADA.

    ejecutar_operacion(
        "8. Cancelar reserva procesada",
        lambda: sistema.obtener_reserva("R001").cancelar()
    )

    # OPERACION 9: CREAR RESERVA CON CLIENTE INEXISTENTE.

    ejecutar_operacion(
        "9. Crear reserva con cliente inexistente",
        lambda: sistema.crear_reserva(
            "R002",
            "C999",
            "S001",
            1
        )
    )

    # OPERACION 10: CREAR RESERVA DE EQUIPO.

    ejecutar_operacion(
        "10. Crear reserva de equipo",
        lambda: sistema.crear_reserva(
            "R003",
            "C002",
            "E001",
            2,
            "Alquiler de computadores"
        ).mostrar_informacion()
    )

    # OPERACION 11: CONFIRMAR Y PROCESAR ALQUILER.

    def confirmar_y_procesar_equipo():

        reserva = sistema.obtener_reserva("R003")

        reserva.confirmar()

        costo = reserva.procesar()

        return f"Alquiler procesado. Costo: ${costo:,.2f}"

    ejecutar_operacion(
        "11. Confirmar y procesar alquiler de equipo",
        confirmar_y_procesar_equipo
    )

    # OPERACION 12: CREAR RESERVA DE ASESORIA.

    ejecutar_operacion(
        "12. Crear reserva de asesoria",
        lambda: sistema.crear_reserva(
            "R004",
            "C001",
            "A001",
            3,
            "Asesoria tecnica"
        ).mostrar_informacion()
    )

    # OPERACION 13: CONFIRMAR Y PROCESAR ASESORIA.

    def confirmar_y_procesar_asesoria():

        reserva = sistema.obtener_reserva("R004")

        reserva.confirmar()

        costo = reserva.procesar(descuento=10)

        return f"Asesoria procesada. Costo: ${costo:,.2f}"

    ejecutar_operacion(
        "13. Confirmar y procesar asesoria",
        confirmar_y_procesar_asesoria
    )

    # OPERACION 14: INTENTAR UTILIZAR UN SERVICIO NO DISPONIBLE.

    def probar_servicio_no_disponible():

        sala.cambiar_disponibilidad(False)

        return sistema.crear_reserva(
            "R005",
            "C001",
            "S001",
            1
        )

    ejecutar_operacion(
        "14. Crear reserva con servicio no disponible",
        probar_servicio_no_disponible
    )

    # OPERACION 15: BUSCAR RESERVAS POR CLIENTE.

    ejecutar_operacion(
        "15. Buscar reservas del cliente C001",
        lambda: [
            r.identificador
            for r in sistema.buscar_reservas(cliente_id="C001")
        ]
    )

    # OPERACION 16: BUSCAR RESERVAS POR ESTADO.

    ejecutar_operacion(
        "16. Buscar reservas procesadas",
        lambda: [
            r.identificador
            for r in sistema.buscar_reservas(estado="PROCESADA")
        ]
    )

    # OPERACION 17: BUSCAR UNA RESERVA INEXISTENTE.

    ejecutar_operacion(
        "17. Consultar reserva inexistente",
        lambda: sistema.obtener_reserva("R999")
    )

    # OPERACION 18: INTENTAR CONFIRMAR RESERVA PROCESADA.

    ejecutar_operacion(
        "18. Confirmar nuevamente una reserva procesada",
        lambda: sistema.obtener_reserva("R001").confirmar()
    )

    # ---------------------------------------------------------
    # RESUMEN FINAL
    # ---------------------------------------------------------

    print("\n")
    print("=" * 65)
    print("RESUMEN FINAL DEL SISTEMA")
    print("=" * 65)

    print("\nCLIENTES REGISTRADOS:")
    sistema.listar_clientes()

    print("\nSERVICIOS REGISTRADOS:")
    sistema.listar_servicios()

    print("\nRESERVAS REGISTRADAS:")
    sistema.listar_reservas()

    print("\nTOTAL DE CLIENTES:", len(sistema.clientes))
    print("TOTAL DE SERVICIOS:", len(sistema.servicios))
    print("TOTAL DE RESERVAS:", len(sistema.reservas))

    print("\nLos eventos y errores se guardaron en:")
    print("software_fj.log")

    print("\n")
    print("=" * 65)
    print("FIN DE LA SIMULACION SOFTWARE FJ")
    print("=" * 65)


# =============================================================
# PUNTO DE ENTRADA DEL PROGRAMA
# =============================================================

if __name__ == "__main__":

    try:

        ejecutar_sistema()

    except KeyboardInterrupt:

        print("\nEjecucion interrumpida por el usuario.")

        logger.warning(
            "El usuario interrumpio la ejecucion del sistema."
        )

    except Exception as error:

        print("\nError general del sistema:", error)

        logger.exception(
            "Se produjo un error general en la aplicacion."
        )

    finally:

        print("\nSistema Software FJ finalizado.")
        