from models import Producto, Usuario, Cliente, Administrador, Pedido


class TiendaService:
    """Gestiona usuarios, inventario y pedidos de la tienda."""

    def __init__(self) -> None:
        self.usuarios: dict[str, Usuario] = {}
        self.productos: dict[str, Producto] = {}
        self.pedidos: list[Pedido] = []

    def registrar_usuario(self, tipo: str, nombre: str, email: str,
                          direccion: str | None = None) -> Usuario:
        """Crea un cliente o un administrador y lo guarda."""
        tipo = tipo.lower()
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

    def anadir_producto(self, producto: Producto) -> None:
        """Añade un producto al inventario."""
        self.productos[producto.id] = producto

    def eliminar_producto(self, producto_id: str) -> bool:
        """Elimina un producto por su id. Devuelve False si no existía."""
        return self.productos.pop(producto_id, None) is not None

    def listar_productos(self) -> list[Producto]:
        return list(self.productos.values())

    def realizar_pedido(self, usuario_id: str, items: dict[str, int]) -> Pedido:
        """Crea un pedido si el cliente existe y hay stock de todo.

        items: diccionario {id_producto: cantidad}
        """
        usuario = self.usuarios.get(usuario_id)
        if usuario is None:
            raise ValueError("El usuario no existe")
        if not isinstance(usuario, Cliente):
            raise ValueError("Solo los clientes pueden hacer pedidos")

        # primero se comprueba todo, y solo si esta todo bien se descuenta
        lineas: list[tuple[Producto, int]] = []
        for producto_id, cantidad in items.items():
            producto = self.productos.get(producto_id)
            if producto is None:
                raise ValueError(f"El producto {producto_id} no existe")
            if not producto.hay_stock(cantidad):
                raise ValueError(f"No hay stock suficiente de {producto.nombre}")
            lineas.append((producto, cantidad))

        pedido = Pedido(usuario, lineas)
        for producto, cantidad in lineas:
            producto.actualizar_stock(-cantidad)

        self.pedidos.append(pedido)
        return pedido

    def listar_pedidos_usuario(self, usuario_id: str) -> list[Pedido]:
        """Pedidos de un usuario ordenados por fecha."""
        pedidos = [p for p in self.pedidos if p.cliente.id == usuario_id]
        return sorted(pedidos, key=lambda p: p.fecha)
