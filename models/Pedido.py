import uuid
from datetime import datetime

from .Producto import Producto
from .Usuario import Cliente


class Pedido:
    """Pedido de un cliente con una lista de productos y cantidades."""

    def __init__(self, cliente: Cliente, items: list[tuple[Producto, int]]) -> None:
        self.id: str = str(uuid.uuid4())[:8]
        self.cliente: Cliente = cliente
        self.items: list[tuple[Producto, int]] = items
        self.fecha: datetime = datetime.now()

    def calcular_total(self) -> float:
        """Suma precio * cantidad de cada producto."""
        return sum(producto.precio * cantidad for producto, cantidad in self.items)

    def __str__(self) -> str:
        lineas = [f"Pedido {self.id} - {self.cliente.nombre} ({self.fecha:%d/%m/%Y %H:%M:%S})"]
        for producto, cantidad in self.items:
            lineas.append(f"   {cantidad} x {producto.nombre} ({producto.precio:.2f}€)")
        lineas.append(f"   TOTAL: {self.calcular_total():.2f}€")
        return "\n".join(lineas)
