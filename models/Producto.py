import uuid


class Producto:
    """Producto genérico de la tienda."""

    def __init__(self, nombre: str, precio: float, stock: int) -> None:
        self.id: str = str(uuid.uuid4())[:8]
        self.nombre: str = nombre
        self.precio: float = precio
        self.stock: int = stock

    def hay_stock(self, cantidad: int) -> bool:
        """Devuelve True si hay unidades suficientes."""
        return self.stock >= cantidad

    def actualizar_stock(self, cantidad: int) -> None:
        """Suma o resta unidades (negativo para compras, positivo para reponer)."""
        if self.stock + cantidad < 0:
            raise ValueError(f"No hay stock suficiente de {self.nombre}")
        self.stock += cantidad

    def __str__(self) -> str:
        return f"[{self.id}] {self.nombre} - {self.precio:.2f}€ (stock: {self.stock})"


class ProductoElectronico(Producto):
    """Producto electrónico con garantía."""

    def __init__(self, nombre: str, precio: float, stock: int, garantia_meses: int) -> None:
        super().__init__(nombre, precio, stock)
        self.garantia_meses: int = garantia_meses

    def __str__(self) -> str:
        return f"{super().__str__()} | Garantía: {self.garantia_meses} meses"


class ProductoRopa(Producto):
    """Prenda de ropa con talla y color."""

    def __init__(self, nombre: str, precio: float, stock: int, talla: str, color: str) -> None:
        super().__init__(nombre, precio, stock)
        self.talla: str = talla
        self.color: str = color

    def __str__(self) -> str:
        return f"{super().__str__()} | Talla: {self.talla}, Color: {self.color}"
