from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field, model_validator

from models import Cliente, Usuario


# Campos comunes a la entrada y a la salida (como ItemBase en el ejemplo)
class UsuarioBase(BaseModel):
    nombre: str = Field(min_length=1, examples=["Ana López"])
    email: EmailStr = Field(examples=["ana@mail.com"])
    direccion: Optional[str] = Field(default=None, examples=["Calle Mayor 5, Madrid"])


class UsuarioCreate(UsuarioBase):
    """Datos que envía el cliente HTTP para crear un usuario (petición)."""

    tipo: Literal["cliente", "administrador"] = Field(examples=["cliente"])

    @model_validator(mode="after")
    def cliente_necesita_direccion(self):
        if self.tipo == "cliente" and not self.direccion:
            raise ValueError("Un cliente necesita dirección postal")
        return self


class UsuarioRead(UsuarioBase):
    """Lo que la API devuelve de un usuario (respuesta)."""

    id: str
    es_admin: bool

    # En el ejemplo se usa orm_mode / from_attributes para devolver el objeto
    # directamente. Aquí no basta: es_admin sale de un método (is_admin()) y
    # direccion solo existe en Cliente, así que se traduce a mano.
    @classmethod
    def desde_modelo(cls, usuario: Usuario) -> "UsuarioRead":
        return cls(
            id=usuario.id,
            nombre=usuario.nombre,
            email=usuario.email,
            es_admin=usuario.is_admin(),
            direccion=usuario.direccion if isinstance(usuario, Cliente) else None,
        )
