"""Pruebas de la API con el TestClient de FastAPI.

Ejecutar desde la carpeta del proyecto:  python -m unittest -v
"""
import unittest

from fastapi.testclient import TestClient

from main import app, get_tienda
from services import TiendaService


class ApiTiendaTests(unittest.TestCase):
    def setUp(self):
        # cada test arranca con una tienda vacía
        self.tienda = TiendaService()
        app.dependency_overrides[get_tienda] = lambda: self.tienda
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    # ---------------------------------------------------------------- helpers
    def crear_cliente(self, email="ana@mail.com"):
        r = self.client.post("/usuarios", json={
            "nombre": "Ana López", "email": email,
            "tipo": "cliente", "direccion": "Calle Mayor 5, Madrid",
        })
        self.assertEqual(r.status_code, 201, r.text)
        return r.json()

    def crear_portatil(self, stock=5):
        r = self.client.post("/productos", json={
            "tipo": "electronico", "nombre": "Portátil",
            "precio": 899.99, "stock": stock, "meses_garantia": 24,
        })
        self.assertEqual(r.status_code, 201, r.text)
        return r.json()

    # --------------------------------------------------------------- usuarios
    def test_crear_y_obtener_usuario(self):
        ana = self.crear_cliente()
        self.assertFalse(ana["es_admin"])

        r = self.client.get(f"/usuarios/{ana['id']}")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["email"], "ana@mail.com")

    def test_listar_usuarios(self):
        self.crear_cliente()
        r = self.client.post("/usuarios", json={
            "nombre": "Admin", "email": "admin@tienda.com", "tipo": "administrador",
        })
        self.assertTrue(r.json()["es_admin"])
        self.assertEqual(len(self.client.get("/usuarios").json()), 2)
        # paginación con skip/limit, como en el ejemplo de clase
        self.assertEqual(len(self.client.get("/usuarios?skip=1&limit=10").json()), 1)
        self.assertEqual(len(self.client.get("/usuarios?limit=1").json()), 1)

    def test_usuario_inexistente_da_404(self):
        self.assertEqual(self.client.get("/usuarios/nope").status_code, 404)

    def test_cliente_sin_direccion_da_422(self):
        r = self.client.post("/usuarios", json={
            "nombre": "Luis", "email": "luis@mail.com", "tipo": "cliente",
        })
        self.assertEqual(r.status_code, 422)

    def test_email_invalido_da_422(self):
        r = self.client.post("/usuarios", json={
            "nombre": "Luis", "email": "esto-no-es-un-email",
            "tipo": "administrador",
        })
        self.assertEqual(r.status_code, 422)

    def test_email_repetido_da_409(self):
        self.crear_cliente()
        r = self.client.post("/usuarios", json={
            "nombre": "Otra Ana", "email": "ANA@mail.com",
            "tipo": "cliente", "direccion": "x",
        })
        self.assertEqual(r.status_code, 409)

    # -------------------------------------------------------------- productos
    def test_crear_cada_tipo_de_producto(self):
        p = self.crear_portatil()
        self.assertEqual(p["tipo"], "electronico")
        self.assertEqual(p["meses_garantia"], 24)

        r = self.client.post("/productos", json={
            "tipo": "ropa", "nombre": "Camiseta", "precio": 15,
            "stock": 30, "talla": "M", "color": "Negro",
        })
        self.assertEqual(r.json()["tipo"], "ropa")

        r = self.client.post("/productos", json={
            "tipo": "generico", "nombre": "Taza", "precio": 5, "stock": 10,
        })
        self.assertEqual(r.json()["tipo"], "generico")
        self.assertIsNone(r.json()["talla"])

        self.assertEqual(len(self.client.get("/productos").json()), 3)

    def test_validaciones_de_producto_dan_422(self):
        casos = [
            {"tipo": "electronico", "nombre": "TV", "precio": 300, "stock": 1},
            {"tipo": "ropa", "nombre": "Gorra", "precio": 10, "stock": 1, "talla": "U"},
            {"tipo": "generico", "nombre": "Taza", "precio": 5, "stock": 1, "color": "rojo"},
            {"tipo": "generico", "nombre": "Taza", "precio": -5, "stock": 1},
            {"tipo": "generico", "nombre": "Taza", "precio": 5, "stock": -1},
            {"tipo": "comida", "nombre": "Pan", "precio": 1, "stock": 1},
        ]
        for datos in casos:
            with self.subTest(datos=datos):
                self.assertEqual(self.client.post("/productos", json=datos).status_code, 422)

    def test_buscar_productos(self):
        self.crear_portatil()
        self.client.post("/productos", json={
            "tipo": "generico", "nombre": "Taza", "precio": 5, "stock": 10,
        })
        nombres = [p["nombre"] for p in self.client.get("/productos?buscar=port").json()]
        self.assertEqual(nombres, ["Portátil"])

    def test_obtener_y_eliminar_producto(self):
        p = self.crear_portatil()
        self.assertEqual(self.client.get(f"/productos/{p['id']}").status_code, 200)

        r = self.client.delete(f"/productos/{p['id']}")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"message": "Producto eliminado correctamente"})
        self.assertEqual(self.client.get(f"/productos/{p['id']}").status_code, 404)
        self.assertEqual(self.client.delete(f"/productos/{p['id']}").status_code, 404)

    # ---------------------------------------------------------------- pedidos
    def test_crear_pedido_descuenta_stock(self):
        ana = self.crear_cliente()
        p = self.crear_portatil(stock=5)

        r = self.client.post("/pedidos", json={
            "cliente_id": ana["id"],
            "items": [{"producto_id": p["id"], "cantidad": 2}],
        })
        self.assertEqual(r.status_code, 201, r.text)
        pedido = r.json()
        self.assertEqual(pedido["total"], 1799.98)
        self.assertEqual(pedido["cliente"]["id"], ana["id"])
        self.assertEqual(pedido["items"][0]["subtotal"], 1799.98)

        self.assertEqual(self.client.get(f"/productos/{p['id']}").json()["stock"], 3)

    def test_lineas_repetidas_se_suman(self):
        ana = self.crear_cliente()
        p = self.crear_portatil(stock=5)
        r = self.client.post("/pedidos", json={
            "cliente_id": ana["id"],
            "items": [{"producto_id": p["id"], "cantidad": 1},
                      {"producto_id": p["id"], "cantidad": 2}],
        })
        self.assertEqual(r.json()["items"][0]["cantidad"], 3)

    def test_errores_de_pedido(self):
        ana = self.crear_cliente()
        p = self.crear_portatil(stock=5)
        r = self.client.post("/usuarios", json={
            "nombre": "Admin", "email": "admin@tienda.com", "tipo": "administrador",
        })
        admin = r.json()

        def pedir(cliente_id, producto_id, cantidad):
            return self.client.post("/pedidos", json={
                "cliente_id": cliente_id,
                "items": [{"producto_id": producto_id, "cantidad": cantidad}],
            }).status_code

        self.assertEqual(pedir("nope", p["id"], 1), 404)      # cliente no existe
        self.assertEqual(pedir(ana["id"], "nope", 1), 404)    # producto no existe
        self.assertEqual(pedir(ana["id"], p["id"], 10), 409)  # sin stock
        self.assertEqual(pedir(admin["id"], p["id"], 1), 403) # admin no compra
        self.assertEqual(pedir(ana["id"], p["id"], 0), 422)   # cantidad inválida

        r = self.client.post("/pedidos", json={"cliente_id": ana["id"], "items": []})
        self.assertEqual(r.status_code, 422)                  # pedido vacío

        # ningún intento fallido ha tocado el stock
        self.assertEqual(self.client.get(f"/productos/{p['id']}").json()["stock"], 5)

    def test_historial_de_pedidos(self):
        ana = self.crear_cliente()
        luis = self.crear_cliente(email="luis@mail.com")
        p = self.crear_portatil(stock=5)
        for cliente, cantidad in [(ana, 1), (luis, 1), (ana, 2)]:
            self.client.post("/pedidos", json={
                "cliente_id": cliente["id"],
                "items": [{"producto_id": p["id"], "cantidad": cantidad}],
            })

        r = self.client.get(f"/usuarios/{ana['id']}/pedidos")
        self.assertEqual(r.status_code, 200)
        self.assertEqual([x["items"][0]["cantidad"] for x in r.json()], [1, 2])
        self.assertEqual(self.client.get("/usuarios/nope/pedidos").status_code, 404)


class CorsTests(unittest.TestCase):
    def test_cors_permite_peticiones_del_frontend(self):
        client = TestClient(app)
        r = client.get("/productos", headers={"Origin": "http://localhost:5500"})
        self.assertEqual(r.headers.get("access-control-allow-origin"), "*")
        r = client.options("/pedidos", headers={
            "Origin": "null",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        })
        self.assertEqual(r.status_code, 200)


if __name__ == "__main__":
    unittest.main()
