"""Punto de entrada y capa de exposición de la tienda online.

Sigue el mismo esquema que el ejemplo de clase (fast-api-uie):
  - los endpoints reciben datos validados por los esquemas Pydantic,
  - obtienen el servicio con Depends(...),
  - llaman a TiendaService (equivalente a crud.py del ejemplo),
  - y si algo falla lanzan HTTPException con el código adecuado.

Arrancar (solo este equipo):        uvicorn main:app --reload
Arrancar (accesible desde la red):  uvicorn main:app --host 0.0.0.0 --port 8000 --reload
Probar:                             http://127.0.0.1:8000/docs
"""

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import (
    PedidoCreate,
    PedidoRead,
    ProductoCreate,
    ProductoRead,
    UsuarioCreate,
    UsuarioRead,
)
from services import Conflicto, OperacionNoPermitida, RecursoNoEncontrado, TiendaService

app = FastAPI(title="Tienda online", version="1.0.0")

# CORS (Práctica 2, parte 2): el navegador bloquea por seguridad las peticiones
# de una página web a un servidor con distinto origen (otro puerto, otra IP o
# un fichero abierto con doble clic). Con esto la API le dice al navegador
# que acepte peticiones del frontend venga de donde venga.
# En una aplicación real se pondría la lista concreta de orígenes permitidos.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Una única tienda en memoria (en el ejemplo, la base de datos SQLite).
# Los datos se pierden al reiniciar el servidor.
tienda_global = TiendaService()


# Dependencia para obtener el servicio (equivalente a get_db en el ejemplo)
def get_tienda():
    return tienda_global


# ------------------------------------------------------------------ Usuarios
@app.post("/usuarios", response_model=UsuarioRead, status_code=201)
def create_usuario(usuario: UsuarioCreate, tienda: TiendaService = Depends(get_tienda)):
    try:
        db_usuario = tienda.registrar_usuario(
            usuario.tipo, usuario.nombre, usuario.email, usuario.direccion
        )
    except Conflicto as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return UsuarioRead.desde_modelo(db_usuario)


@app.get("/usuarios", response_model=list[UsuarioRead])
def read_usuarios(skip: int = 0, limit: int = 10,
                  tienda: TiendaService = Depends(get_tienda)):
    usuarios = tienda.listar_usuarios(skip=skip, limit=limit)
    return [UsuarioRead.desde_modelo(u) for u in usuarios]


@app.get("/usuarios/{usuario_id}", response_model=UsuarioRead)
def read_usuario(usuario_id: str, tienda: TiendaService = Depends(get_tienda)):
    db_usuario = tienda.obtener_usuario(usuario_id)
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return UsuarioRead.desde_modelo(db_usuario)


@app.get("/usuarios/{cliente_id}/pedidos", response_model=list[PedidoRead])
def read_pedidos_cliente(cliente_id: str, tienda: TiendaService = Depends(get_tienda)):
    if tienda.obtener_usuario(cliente_id) is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    pedidos = tienda.listar_pedidos_usuario(cliente_id)
    return [PedidoRead.desde_modelo(p) for p in pedidos]


# ----------------------------------------------------------------- Productos
@app.post("/productos", response_model=ProductoRead, status_code=201)
def create_producto(producto: ProductoCreate, tienda: TiendaService = Depends(get_tienda)):
    try:
        db_producto = tienda.crear_producto(
            tipo=producto.tipo,
            nombre=producto.nombre,
            precio=producto.precio,
            stock=producto.stock,
            meses_garantia=producto.meses_garantia,
            talla=producto.talla,
            color=producto.color,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ProductoRead.desde_modelo(db_producto)


@app.get("/productos", response_model=list[ProductoRead])
def read_productos(skip: int = 0, limit: int = 10, buscar: str | None = None,
                   tienda: TiendaService = Depends(get_tienda)):
    if buscar:
        # extra: /productos?buscar=port reutiliza buscar_productos del servicio
        productos = tienda.buscar_productos(buscar)[skip:skip + limit]
    else:
        productos = tienda.listar_productos(skip=skip, limit=limit)
    return [ProductoRead.desde_modelo(p) for p in productos]


@app.get("/productos/{producto_id}", response_model=ProductoRead)
def read_producto(producto_id: str, tienda: TiendaService = Depends(get_tienda)):
    db_producto = tienda.obtener_producto(producto_id)
    if db_producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return ProductoRead.desde_modelo(db_producto)


@app.delete("/productos/{producto_id}")
def delete_producto(producto_id: str, tienda: TiendaService = Depends(get_tienda)):
    result = tienda.eliminar_producto(producto_id)
    if not result:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"message": "Producto eliminado correctamente"}


# ------------------------------------------------------------------- Pedidos
@app.post("/pedidos", response_model=PedidoRead, status_code=201)
def create_pedido(pedido: PedidoCreate, tienda: TiendaService = Depends(get_tienda)):
    # el servicio espera {producto_id: cantidad}; si el mismo producto viene
    # en varias líneas, sumo las cantidades en vez de pisar la anterior
    items: dict[str, int] = {}
    for linea in pedido.items:
        items[linea.producto_id] = items.get(linea.producto_id, 0) + linea.cantidad

    try:
        db_pedido = tienda.realizar_pedido(pedido.cliente_id, items)
    except RecursoNoEncontrado as e:      # no existe el cliente o un producto
        raise HTTPException(status_code=404, detail=str(e))
    except OperacionNoPermitida as e:     # un administrador no puede comprar
        raise HTTPException(status_code=403, detail=str(e))
    except Conflicto as e:                # no hay stock suficiente
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:               # cualquier otro dato inválido
        raise HTTPException(status_code=400, detail=str(e))
    return PedidoRead.desde_modelo(db_pedido)


if __name__ == "__main__":
    # Permite arrancar con el botón Run de VS Code o con: python main.py
    # host="0.0.0.0" -> acepta conexiones de otros equipos de la red local
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
