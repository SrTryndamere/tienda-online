"""Cliente de la API de la tienda (Práctica 2 - parte 2, partes 1 y 2).

Este script es INDEPENDIENTE del servidor: no importa nada de models/,
services/ ni main.py. Todo lo hace con peticiones HTTP usando `requests`,
igual que haría cualquier otro programa (o persona) desde otro ordenador.

Uso:
    python cliente.py                              -> usa BASE_URL de abajo
    python cliente.py http://192.168.1.34:8000     -> usa la API de otro equipo
"""
import sys
import uuid

import requests

# ---------------------------------------------------------------------------
# Dirección de la API. Cámbiala aquí (o pásala como argumento al ejecutar).
#   - Misma máquina:   "http://localhost:8000"
#   - Otro equipo:     "http://<IP del servidor>:8000"   (ej. http://192.168.1.34:8000)
# ---------------------------------------------------------------------------
BASE_URL = "http://localhost:8000"

TIMEOUT = 5  # segundos máximos esperando respuesta

try:
    sys.stdout.reconfigure(encoding="utf-8")  # para que se vean bien ✔ y tildes en Windows
except Exception:
    pass


# ---------------------------------------------------------------------------
# Función auxiliar: comprueba el código HTTP y devuelve el JSON de la respuesta
# ---------------------------------------------------------------------------
def comprobar(respuesta, codigo_esperado, descripcion):
    """Si el código HTTP no es el esperado, enseña el error y para el programa.
    Si es correcto, devuelve el cuerpo de la respuesta convertido de JSON a Python."""
    if respuesta.status_code != codigo_esperado:
        print(f"✘ {descripcion}: esperaba {codigo_esperado} y la API devolvió {respuesta.status_code}")
        print(f"  Detalle: {respuesta.text}")
        sys.exit(1)
    print(f"✔ {descripcion}  [{respuesta.request.method} {respuesta.url} -> {respuesta.status_code}]")
    return respuesta.json()   # JSON -> listas y diccionarios de Python


# ---------------------------------------------------------------------------
# Una función por operación de la API
# ---------------------------------------------------------------------------
def crear_usuario(nombre, email, tipo="cliente", direccion=None):
    datos = {"nombre": nombre, "email": email, "tipo": tipo, "direccion": direccion}
    r = requests.post(f"{BASE_URL}/usuarios", json=datos, timeout=TIMEOUT)   # POST /usuarios
    return comprobar(r, 201, f"Crear usuario {nombre}")


def listar_usuarios():
    r = requests.get(f"{BASE_URL}/usuarios", params={"limit": 100}, timeout=TIMEOUT)  # GET /usuarios?limit=100
    return comprobar(r, 200, "Listar usuarios")


def crear_producto(datos):
    r = requests.post(f"{BASE_URL}/productos", json=datos, timeout=TIMEOUT)  # POST /productos
    return comprobar(r, 201, f"Crear producto {datos['nombre']}")


def listar_productos():
    r = requests.get(f"{BASE_URL}/productos", params={"limit": 100}, timeout=TIMEOUT)  # GET /productos
    return comprobar(r, 200, "Listar productos")


def crear_pedido(cliente_id, items):
    """items: lista de (producto_id, cantidad)"""
    datos = {
        "cliente_id": cliente_id,
        "items": [{"producto_id": pid, "cantidad": cant} for pid, cant in items],
    }
    r = requests.post(f"{BASE_URL}/pedidos", json=datos, timeout=TIMEOUT)  # POST /pedidos
    return comprobar(r, 201, "Crear pedido")


def pedidos_de_usuario(usuario_id):
    r = requests.get(f"{BASE_URL}/usuarios/{usuario_id}/pedidos", timeout=TIMEOUT)  # GET /usuarios/{id}/pedidos
    return comprobar(r, 200, "Consultar pedidos del usuario")


# ---------------------------------------------------------------------------
# Flujo de prueba
# ---------------------------------------------------------------------------
def main():
    global BASE_URL
    if len(sys.argv) > 1:                     # python cliente.py http://192.168.1.34:8000
        BASE_URL = sys.argv[1].rstrip("/")

    print(f"Usando la API en: {BASE_URL}\n")

    # 0. ¿Responde el servidor?
    try:
        requests.get(f"{BASE_URL}/docs", timeout=TIMEOUT)
    except requests.exceptions.ConnectionError:
        print("✘ No se puede conectar con la API. Comprueba que:")
        print("  - el servidor está arrancado (uvicorn main:app --host 0.0.0.0 --port 8000)")
        print("  - la IP y el puerto de BASE_URL son correctos")
        print("  - el firewall del equipo servidor permite conexiones al puerto 8000")
        sys.exit(1)

    # El email tiene que ser único: le añado un número distinto en cada ejecución
    sufijo = uuid.uuid4().hex[:6]

    # 1. Crear un usuario
    print("== 1. Crear un usuario ==")
    ana = crear_usuario("Ana López", f"ana{sufijo}@mail.com", direccion="Calle Mayor 5, Madrid")
    print(f"   Creado con id {ana['id']}\n")

    # 2. Consultar la lista de usuarios
    print("== 2. Lista de usuarios ==")
    for u in listar_usuarios():
        tipo = "admin" if u["es_admin"] else "cliente"
        print(f"   [{u['id']}] {u['nombre']} ({u['email']}) - {tipo}")
    print()

    # 3. Crear varios productos
    print("== 3. Crear productos ==")
    portatil = crear_producto({"tipo": "electronico", "nombre": "Portátil", "precio": 899.99,
                               "stock": 5, "meses_garantia": 24})
    camiseta = crear_producto({"tipo": "ropa", "nombre": "Camiseta", "precio": 15.0,
                               "stock": 30, "talla": "M", "color": "Negro"})
    taza = crear_producto({"tipo": "generico", "nombre": "Taza", "precio": 6.5, "stock": 12})
    print()

    # 4. Consultar la lista de productos
    print("== 4. Lista de productos ==")
    for p in listar_productos():
        print(f"   [{p['id']}] {p['nombre']:<12} {p['precio']:>8.2f}€  stock {p['stock']:>3}  ({p['tipo']})")
    print()

    # 5. Crear un pedido para el usuario
    print("== 5. Crear un pedido ==")
    pedido = crear_pedido(ana["id"], [(portatil["id"], 1), (camiseta["id"], 2), (taza["id"], 3)])
    for linea in pedido["items"]:
        print(f"   {linea['cantidad']} x {linea['nombre']:<10} = {linea['subtotal']:.2f}€")
    print(f"   TOTAL: {pedido['total']:.2f}€\n")

    # 6. Consultar los pedidos del usuario
    print(f"== 6. Pedidos de {ana['nombre']} ==")
    for p in pedidos_de_usuario(ana["id"]):
        print(f"   Pedido {p['id']} ({p['fecha'][:19]}): {len(p['items'])} líneas, total {p['total']:.2f}€")
    print()

    # 7. Extra: comprobar que la API gestiona los errores con su código HTTP
    print("== 7. Extra: errores controlados ==")
    r = requests.post(f"{BASE_URL}/pedidos", timeout=TIMEOUT,
                      json={"cliente_id": ana["id"], "items": [{"producto_id": portatil["id"], "cantidad": 1000}]})
    print(f"   Pedido sin stock suficiente -> {r.status_code} ({r.json()['detail']})")
    r = requests.get(f"{BASE_URL}/usuarios/no-existe", timeout=TIMEOUT)
    print(f"   Usuario inexistente         -> {r.status_code} ({r.json()['detail']})")
    r = requests.post(f"{BASE_URL}/productos", json={"tipo": "ropa", "nombre": "Gorra", "precio": 10, "stock": 1},
                      timeout=TIMEOUT)
    print(f"   Ropa sin talla ni color     -> {r.status_code} (validación de Pydantic)")

    print("\nFlujo completado ✔")


if __name__ == "__main__":
    main()
