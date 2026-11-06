import uuid


class Usuario:
    def __init__(self, nombre, email):
        self.id = str(uuid.uuid4())[:8]
        self.nombre = nombre
        self.email = email

    def is_admin(self):
        return False

    def __str__(self):
        return f"[{self.id}] {self.nombre} ({self.email})"


class Cliente(Usuario):
    def __init__(self, nombre, email, direccion):
        super().__init__(nombre, email)
        self.direccion = direccion

    def __str__(self):
        return f"{super().__str__()} - {self.direccion}"


class Administrador(Usuario):
    # de momento solo se diferencia del usuario normal en esto
    def is_admin(self):
        return True
