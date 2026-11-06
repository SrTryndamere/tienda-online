from datetime import datetime

from pydantic import BaseModel, Field

from models import Pedido
from schemas.usuario import UsuarioRead


# Campos comunes de una línea de pedido
class PedidoItemBase(BaseModel):
    producto_id: str = Field(examples=["a1b2c3d4"])
    cantidad: int = Field(gt=0, examples=[2])


class PedidoItemCreate(PedidoItemBase):
    """Una línea del pedido tal y como la manda el cliente."""


class PedidoItemRead(PedidoItemBase):
    nombre: str
    precio_unitario: float
    subtotal: float


class PedidoCreate(BaseModel):
    cliente_id: str = Field(examples=["e5f6a7b8"])
    items: list[PedidoItemCreate] = Field(min_length=1)


class PedidoRead(BaseModel):
    id: str
    fecha: datetime
    cliente: UsuarioRead
    total: float
    items: list[PedidoItemRead]

    @classmethod
    def desde_modelo(cls, pedido: Pedido) -> "PedidoRead":
        items = [
            PedidoItemRead(
                producto_id=producto.id,
                nombre=producto.nombre,
                precio_unitario=producto.precio,
                cantidad=cantidad,
                subtotal=round(producto.precio * cantidad, 2),
            )
            for producto, cantidad in pedido.items
        ]
        return cls(
            id=pedido.id,
            fecha=pedido.fecha,
            cliente=UsuarioRead.desde_modelo(pedido.cliente),
            total=round(pedido.calcular_total(), 2),
            items=items,
        )
