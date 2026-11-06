import uuid


class Producto:
    def __init__(self, nombre, precio, stock):
        self.id = str(uuid.uuid4())[:8]
        self.nombre = nombre
        self.precio = precio
        self.stock = stock

    def hay_stock(self, cantidad):
        return self.stock >= cantidad

    def actualizar_stock(self, cantidad):
        # cantidad negativa = venta, positiva = reposicion
        if self.stock + cantidad < 0:
            raise ValueError(f"No hay stock suficiente de {self.nombre}")
        self.stock += cantidad

    def __str__(self):
        return f"[{self.id}] {self.nombre} - {self.precio:.2f}€ (stock: {self.stock})"


class ProductoElectronico(Producto):
    def __init__(self, nombre, precio, stock, garantia_meses):
        super().__init__(nombre, precio, stock)
        self.garantia_meses = garantia_meses

    def __str__(self):
        return super().__str__() + f" | Garantía: {self.garantia_meses} meses"


class ProductoRopa(Producto):
    def __init__(self, nombre, precio, stock, talla, color):
        super().__init__(nombre, precio, stock)
        self.talla = talla
        self.color = color

    def __str__(self):
        return super().__str__() + f" | Talla: {self.talla}, Color: {self.color}"
