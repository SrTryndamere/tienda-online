import uuid


class Usuario:
    """Usuario básico de la tienda."""

    def __init__(self, nombre: str, email: str) -> None:
        self.id: str = str(uuid.uuid4())[:8]
        self.nombre: str = nombre
        self.email: str = email

    def is_admin(self) -> bool:
        return False

    def __str__(self) -> str:
        return f"[{self.id}] {self.nombre} ({self.email})"


class Cliente(Usuario):
    """Cliente que puede hacer pedidos."""

    def __init__(self, nombre: str, email: str, direccion: str) -> None:
        super().__init__(nombre, email)
        self.direccion: str = direccion

    def __str__(self) -> str:
        return f"{super().__str__()} - {self.direccion}"


class Administrador(Usuario):
    """Gestor de la tienda."""

    def is_admin(self) -> bool:
        return True
