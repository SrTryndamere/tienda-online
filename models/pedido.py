import uuid
from datetime import datetime


class Pedido:
    def __init__(self, cliente, items):
        # items es una lista de tuplas (producto, cantidad)
        self.id = str(uuid.uuid4())[:8]
        self.cliente = cliente
        self.items = items
        self.fecha = datetime.now()

    def calcular_total(self):
        total = 0
        for producto, cantidad in self.items:
            total += producto.precio * cantidad
        return total

    def __str__(self):
        texto = f"Pedido {self.id} - {self.cliente.nombre} ({self.fecha:%d/%m/%Y %H:%M:%S})\n"
        for producto, cantidad in self.items:
            texto += f"   {cantidad} x {producto.nombre} ({producto.precio:.2f}€)\n"
        texto += f"   TOTAL: {self.calcular_total():.2f}€"
        return texto
