# Tienda online – API REST y clientes (Práctica 2, Unidad II)

**Autor:** Gabriel Gascón

API REST con FastAPI que expone la lógica de `TiendaService` (Práctica 1), y tres formas
de consumirla (parte 2): Swagger (`/docs`), un cliente Python con `requests` y un frontend web.

## Estructura

```
P2/
├── models/          # tienda de la PRÁCTICA 1: dominio (idéntico a la práctica 1)
├── services/        # tienda de la PRÁCTICA 1: TiendaService (ampliado) + excepciones propias
├── schemas/         # esquemas Pydantic de entrada (Create) y salida (Read)
├── tests/           # tests del servicio y de la API
├── main.py          # capa de exposición: app FastAPI, endpoints y CORS
├── demo_practica1.py # el main.py por consola de la práctica 1, funcionando sobre el mismo código
├── cliente/
│   └── cliente.py   # PARTE 2.1: cliente HTTP con requests (independiente del servidor)
├── frontend/
│   └── index.html   # PARTE 2.3: frontend web (HTML + JavaScript con fetch)
└── requirements.txt
```

## Cómo ejecutarlo

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload     # o: python main.py
```

Swagger: http://127.0.0.1:8000/docs

`--host 0.0.0.0` hace que la API acepte conexiones de otros equipos de la red.
Sin él (por defecto `127.0.0.1`) solo se puede usar desde el propio ordenador.

Tests: `python -m unittest -v` (desde la carpeta P2)

## Endpoints

| Método | Ruta | Respuesta OK |
|---|---|---|
| POST | /usuarios | 201 + UsuarioRead |
| GET | /usuarios (`skip`, `limit`) | 200 + lista |
| GET | /usuarios/{usuario_id} | 200 |
| GET | /usuarios/{cliente_id}/pedidos | 200 + lista de PedidoRead |
| POST | /productos | 201 + ProductoRead |
| GET | /productos (`skip`, `limit`, `buscar` opcional) | 200 + lista |
| GET | /productos/{producto_id} | 200 |
| DELETE | /productos/{producto_id} | 200 + `{"message": ...}` |
| POST | /pedidos | 201 + PedidoRead |

## Códigos de error

Siguiendo el ejemplo de clase (`fast-api-uie`), cada endpoint lanza `HTTPException`:
el servicio devuelve `None`/`False` cuando algo no existe (como `crud.py`) o lanza una
excepción de negocio que el endpoint captura y traduce.

| Código | Cuándo | Origen |
|---|---|---|
| 422 | Datos mal formados (email inválido, precio ≤ 0, falta talla en ropa...) | Pydantic (automático) |
| 404 | Usuario o producto inexistente | `None`/`False` del servicio o `RecursoNoEncontrado` |
| 409 | Stock insuficiente, email repetido | `Conflicto` |
| 403 | Un administrador intenta hacer un pedido | `OperacionNoPermitida` |
| 400 | Cualquier otro `ValueError` de negocio | `ValueError` |

## Relación con la tienda de la práctica 1

La API **no reimplementa la tienda**: usa directamente el código de la práctica 1.

| Práctica 1 | En este proyecto | Cambios |
|---|---|---|
| `models/` (`Producto`, `ProductoElectronico`, `ProductoRopa`, `Usuario`, `Cliente`, `Administrador`, `Pedido`) | `models/` | Ninguno: ficheros idénticos |
| `services/tienda_service.py` (`TiendaService`) | `services/tienda_service.py` | Ampliado (ver abajo); los métodos originales siguen funcionando igual |
| `main.py` (demo por consola) | `demo_practica1.py` | Ninguno: se ejecuta tal cual (`python demo_practica1.py`) |
| — | `schemas/` + `main.py` | Nuevo: capa REST con FastAPI encima de `TiendaService` |

## Cambios respecto a la práctica 1

- `TiendaService`: nuevos `obtener_usuario` y `obtener_producto` (devuelven `None` si no
  existe), `listar_usuarios`/`listar_productos` con `skip` y `limit`, y `crear_producto` (fábrica por tipo, igual que `registrar_usuario`); email único.
- `services/excepciones.py`: excepciones propias (heredan de `ValueError`, así el
  código antiguo sigue funcionando) para poder devolver el código HTTP correcto.
- Esquemas con el patrón `XBase` → `XCreate` / `XRead` del ejemplo de clase.
- Los datos viven en memoria: se pierden al reiniciar el servidor.


---

# Práctica 2 · Parte 2: consumir la API desde distintos clientes

Los tres clientes usan **los mismos endpoints** y trabajan sobre **los mismos datos**:
lo que crea uno lo ven los otros (mientras el servidor siga encendido).

## Parte 1 · Cliente Python (`cliente/cliente.py`)

No importa nada del servidor: todo va por HTTP con `requests`.

```bash
cd cliente
python cliente.py                              # usa BASE_URL = http://localhost:8000
python cliente.py http://192.168.1.34:8000     # otra dirección sin tocar el código
```

Flujo: crear usuario → listar usuarios → crear 3 productos → listar productos → crear pedido →
pedidos del usuario, y un extra que provoca errores (409, 404, 422) para ver que la API los gestiona.

Cada petición pasa por `comprobar(respuesta, codigo_esperado, descripcion)`, que verifica el
código HTTP y devuelve `respuesta.json()` (JSON → listas y diccionarios de Python).

| Función | Petición |
|---|---|
| `crear_usuario` | `POST /usuarios` → 201 |
| `listar_usuarios` | `GET /usuarios?limit=100` → 200 |
| `crear_producto` | `POST /productos` → 201 |
| `listar_productos` | `GET /productos?limit=100` → 200 |
| `crear_pedido` | `POST /pedidos` → 201 |
| `pedidos_de_usuario` | `GET /usuarios/{id}/pedidos` → 200 |

## Parte 2 · Comunicación entre dos equipos

**Equipo servidor** (el que ejecuta la API):

1. Conectar los dos equipos **a la misma red** (misma wifi; ojo, algunas redes de universidad
   aíslan a los dispositivos entre sí; si no conecta, probad con el punto de acceso del móvil).
2. Ver su IP local: en la terminal `ipconfig` → **Dirección IPv4** (ej. `192.168.1.34`).
   En Mac/Linux: `ipconfig getifaddr en0` / `hostname -I`.
3. Arrancar la API escuchando en la red: `uvicorn main:app --host 0.0.0.0 --port 8000`.
4. Si Windows pregunta por el **firewall**, **Permitir acceso** (marcar redes privadas).
   Si no pregunta y no conecta: *Firewall de Windows Defender → Permitir una aplicación* → Python.

**Equipo cliente**:

1. `python cliente.py http://192.168.1.34:8000` (o cambiar `BASE_URL` en el fichero).
2. Abrir en el navegador `http://192.168.1.34:8000/docs`.
3. Comprobar en la terminal del servidor que aparecen las peticiones con la IP del cliente:
   `INFO: 192.168.1.50:54321 - "POST /usuarios HTTP/1.1" 201 Created`.

| | `localhost` / `127.0.0.1` | IP local (`192.168.x.x`) |
|---|---|---|
| Significa | "este mismo ordenador" | "el ordenador con esa dirección en la red" |
| Desde otro equipo | apunta a **sí mismo**, no al servidor | llega al servidor |
| Servidor necesario | `uvicorn main:app` | `uvicorn main:app --host 0.0.0.0` |

## Parte 3 · Frontend (`frontend/index.html`)

HTML + JavaScript sin frameworks. Para abrirlo:

- doble clic en `index.html`, o
- `cd frontend && python -m http.server 5500` → http://localhost:5500

La dirección de la API se cambia arriba a la derecha (campo **API** + **Conectar**), así que
sirve igual contra la API local o contra la de un compañero (`http://192.168.1.34:8000`).

### Cómo explicar el código

- **Todas** las peticiones pasan por la función `api(metodo, ruta, cuerpo)`: hace el `fetch`,
  convierte el cuerpo a JSON (`JSON.stringify`), lee la respuesta (`respuesta.json()`) y, si el
  código no es 2xx (`respuesta.ok`), lanza un error con el `detail` que devuelve FastAPI.
- Cada llamada está marcada con un comentario `// PETICIÓN → ...`:

| Acción en la página | Función JS | Endpoint | Qué se hace con la respuesta |
|---|---|---|---|
| Ver productos / buscar | `cargarProductos` | `GET /productos?limit=100&buscar=...` | pinta la tabla y rellena el desplegable del pedido |
| Crear producto | `crearProducto` | `POST /productos` | aviso verde y recarga la lista |
| Ver usuarios | `cargarUsuarios` | `GET /usuarios?limit=100` | pinta la tabla y los desplegables |
| Crear usuario | `crearUsuario` | `POST /usuarios` | aviso y recarga |
| Realizar pedido | `enviarPedido` | `POST /pedidos` | aviso con el total; recarga productos (el stock cambia) |
| Pedidos de un usuario | `cargarHistorial` | `GET /usuarios/{id}/pedidos` | pinta cada pedido con sus líneas |

- Errores: 422 (validación de Pydantic, viene como lista) y 404/409/403 (vienen como texto) se
  muestran en el aviso rojo de abajo; `textoDeError` convierte los dos formatos en un mensaje.

### CORS (el único cambio en el servidor)

El navegador, por seguridad, bloquea las peticiones de una página a un servidor con **distinto
origen** (otro puerto, otra IP o un fichero abierto con doble clic). Por eso `main.py` añade
`CORSMiddleware` con `allow_origins=["*"]`: la API le indica al navegador que acepte esas
peticiones. Sin esto, el frontend daría un error de CORS en la consola (F12), aunque Swagger
y el cliente Python funcionarían igual (CORS solo lo aplican los navegadores).

---

# Docker (Práctica 3.2)

La API está contenerizada con un `Dockerfile` basado en `python:3.12-slim`. La imagen
instala las dependencias de `requirements.txt` (versiones fijadas), copia el código y
arranca la API con `uvicorn` como un usuario sin privilegios (`appuser`), no como root.
El fichero `.dockerignore` evita copiar a la imagen cachés, tests, `.git` y configuración local.

## Construir la imagen

```bash
docker build -t tienda-online:1.0 .
```

## Ejecutar el contenedor

```bash
docker run -d -p 8000:8000 --name tienda tienda-online:1.0
```

- `-d`: en segundo plano.
- `-p 8000:8000`: puerto del ordenador → puerto del contenedor. Para usar otro puerto en el
  ordenador, cambia el primero (ej. `-p 9000:8000` → http://localhost:9000/docs).
- `--name tienda`: nombre del contenedor.

Comandos útiles:

```bash
docker ps                 # ver contenedores en marcha
docker logs tienda        # ver la salida de la API
docker stop tienda        # parar
docker rm tienda          # borrar el contenedor (la imagen se mantiene)
```

## Descargar la imagen desde Docker Hub

No hace falta clonar el repositorio ni tener Python instalado, solo Docker:

```bash
docker pull srtryndamere/tienda-online:latest
docker run -d -p 8000:8000 --name tienda srtryndamere/tienda-online:latest
```

Imagen publicada: https://hub.docker.com/r/srtryndamere/tienda-online
(etiquetas `1.0` y `latest`).

## Variables de entorno

No se necesita ninguna: la API no usa base de datos ni claves. El puerto se configura con
`-p` al ejecutar el contenedor.

## Salida esperada y pruebas

`docker logs tienda` debe mostrar:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Pasos de prueba en http://localhost:8000/docs:

| Prueba | Endpoint | Resultado esperado |
|---|---|---|
| Listar productos (vacío al arrancar) | `GET /productos` | 200 + `[]` |
| Crear usuario | `POST /usuarios` | 201 + usuario con su `id` |
| Repetir el mismo email | `POST /usuarios` | 409 (email repetido) |
| Usuario inexistente | `GET /usuarios/abc` | 404 |
| Email inválido | `POST /usuarios` con `"email": "hola"` | 422 |

Los datos se guardan en memoria: al parar o borrar el contenedor se pierden.