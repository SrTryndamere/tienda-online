from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator

from models import Producto, ProductoElectronico, ProductoRopa

TipoProducto = Literal["generico", "electronico", "ropa"]


# Campos comunes a la entrada y a la salida
class ProductoBase(BaseModel):
    tipo: TipoProducto = Field(examples=["electronico"])
    nombre: str = Field(min_length=1, examples=["Portátil"])
    precio: float = Field(gt=0, examples=[899.99])
    stock: int = Field(ge=0, examples=[5])
    # solo electrónicos
    meses_garantia: Optional[int] = Field(default=None, gt=0, examples=[24])
    # solo ropa
    talla: Optional[str] = Field(default=None, min_length=1, examples=[None])
    color: Optional[str] = Field(default=None, min_length=1, examples=[None])


class ProductoCreate(ProductoBase):
    """Datos para crear un producto. Los campos extra dependen del tipo."""

    @model_validator(mode="after")
    def validar_campos_segun_tipo(self):
        es_electronico = self.tipo == "electronico"
        es_ropa = self.tipo == "ropa"

        if es_electronico and self.meses_garantia is None:
            raise ValueError("Un producto electrónico necesita 'meses_garantia'")
        if es_ropa and (self.talla is None or self.color is None):
            raise ValueError("Un producto de ropa necesita 'talla' y 'color'")

        # tampoco dejo mandar campos que no pintan nada para ese tipo
        if not es_electronico and self.meses_garantia is not None:
            raise ValueError("'meses_garantia' solo aplica a productos electrónicos")
        if not es_ropa and (self.talla is not None or self.color is not None):
            raise ValueError("'talla' y 'color' solo aplican a productos de ropa")
        return self


class ProductoRead(ProductoBase):
    """Lo que la API devuelve de un producto."""

    id: str

    # 'tipo' no es un atributo del modelo (se deduce de la clase) y la garantía
    # se llama garantia_meses en el modelo, así que se traduce a mano.
    @classmethod
    def desde_modelo(cls, producto: Producto) -> "ProductoRead":
        datos = {
            "id": producto.id,
            "nombre": producto.nombre,
            "precio": producto.precio,
            "stock": producto.stock,
        }
        # ojo al orden: las subclases antes que la clase base
        if isinstance(producto, ProductoElectronico):
            datos["tipo"] = "electronico"
            datos["meses_garantia"] = producto.garantia_meses
        elif isinstance(producto, ProductoRopa):
            datos["tipo"] = "ropa"
            datos["talla"] = producto.talla
            datos["color"] = producto.color
        else:
            datos["tipo"] = "generico"
        return cls(**datos)
