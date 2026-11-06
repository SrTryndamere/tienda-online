from models import (
    Administrador,
    Cliente,
    Pedido,
    Producto,
    ProductoElectronico,
    ProductoRopa,
)
from services.excepciones import Conflicto, OperacionNoPermitida, RecursoNoEncontrado


class TiendaService:
    def __init__(self):
        self.usuarios = {}   # id -> Usuario
        self.productos = {}  # id -> Producto
        self.pedidos = []

    # ------------------------------------------------------------------ usuarios
    def registrar_usuario(self, tipo, nombre, email, direccion=None):
        tipo = tipo.lower()

        # no dejo registrar dos usuarios con el mismo email
        if any(u.email.lower() == email.lower() for u in self.usuarios.values()):
            raise Conflicto(f"Ya existe un usuario con el email {email}")

        if tipo == "cliente":
            if direccion is None:
                raise ValueError("Un cliente necesita dirección")
            usuario = Cliente(nombre, email, direccion)
        elif tipo == "administrador":
            usuario = Administrador(nombre, email)
        else:
            raise ValueError(f"Tipo de usuario no válido: {tipo}")

        self.usuarios[usuario.id] = usuario
        return usuario

    def obtener_usuario(self, usuario_id):
        # igual que crud.get_item del ejemplo: None si no existe
        return self.usuarios.get(usuario_id)

    def listar_usuarios(self, skip: int = 0, limit: int = 10):
        return list(self.usuarios.values())[skip:skip + limit]

    # ----------------------------------------------------------------- productos
    def crear_producto(self, tipo, nombre, precio, stock,
                       meses_garantia=None, talla=None, color=None):
        """Fábrica de productos: igual que registrar_usuario pero para productos.
        Así main.py no necesita conocer las clases concretas del modelo."""
        tipo = tipo.lower()
        if tipo == "generico":
            producto = Producto(nombre, precio, stock)
        elif tipo == "electronico":
            if meses_garantia is None:
                raise ValueError("Un producto electrónico necesita meses de garantía")
            producto = ProductoElectronico(nombre, precio, stock, meses_garantia)
        elif tipo == "ropa":
            if talla is None or color is None:
                raise ValueError("Un producto de ropa necesita talla y color")
            producto = ProductoRopa(nombre, precio, stock, talla, color)
        else:
            raise ValueError(f"Tipo de producto no válido: {tipo}")

        self.anadir_producto(producto)
        return producto

    def anadir_producto(self, producto):
        self.productos[producto.id] = producto

    def obtener_producto(self, producto_id):
        # None si no existe
        return self.productos.get(producto_id)

    def eliminar_producto(self, producto_id):
        # devuelve False si el producto no existia (igual que crud.delete_item)
        return self.productos.pop(producto_id, None) is not None

    def listar_productos(self, skip: int = 0, limit: int | None = None):
        productos = list(self.productos.values())
        if limit is None:
            return productos[skip:]
        return productos[skip:skip + limit]

    def buscar_productos(self, texto: str):
        """Devuelve los productos cuyo nombre contiene el texto indicado."""
        texto = texto.strip().lower()
        if not texto:
            return self.listar_productos()

        return [
            producto for producto in self.productos.values()
            if texto in producto.nombre.lower()
        ]

    # ------------------------------------------------------------------- pedidos
    def realizar_pedido(self, usuario_id, items: dict[str, int]):
        """items tiene la forma {id_producto: cantidad}"""
        usuario = self.obtener_usuario(usuario_id)
        if usuario is None:
            raise RecursoNoEncontrado(f"El usuario {usuario_id} no existe")
        if not isinstance(usuario, Cliente):
            raise OperacionNoPermitida("Solo los clientes pueden hacer pedidos")
        if not items:
            raise ValueError("El pedido tiene que tener al menos un producto")

        # primero compruebo todo y solo si esta bien descuento el stock,
        # asi no se queda un pedido a medias si falla algun producto
        lineas = []
        for producto_id, cantidad in items.items():
            if cantidad <= 0:
                raise ValueError("La cantidad tiene que ser mayor que 0")
            producto = self.obtener_producto(producto_id)
            if producto is None:
                raise RecursoNoEncontrado(f"El producto {producto_id} no existe")
            if not producto.hay_stock(cantidad):
                raise Conflicto(f"No hay stock suficiente de {producto.nombre}")
            lineas.append((producto, cantidad))

        for producto, cantidad in lineas:
            producto.actualizar_stock(-cantidad)

        pedido = Pedido(usuario, lineas)
        self.pedidos.append(pedido)
        return pedido

    def listar_pedidos_usuario(self, usuario_id):
        pedidos = [p for p in self.pedidos if p.cliente.id == usuario_id]
        pedidos.sort(key=lambda p: p.fecha)  # del mas antiguo al mas reciente
        return pedidos
