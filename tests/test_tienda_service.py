import unittest

from models import ProductoElectronico, ProductoRopa
from services import TiendaService


class TiendaServiceTests(unittest.TestCase):
    def test_buscar_productos_por_nombre(self):
        tienda = TiendaService()

        portatil = ProductoElectronico("Portátil", 899.99, 5, 24)
        auriculares = ProductoElectronico("Auriculares", 59.90, 20, 12)
        camiseta = ProductoRopa("Camiseta", 15.00, 30, "M", "Negro")

        for producto in [portatil, auriculares, camiseta]:
            tienda.anadir_producto(producto)

        resultados = tienda.buscar_productos("port")
        nombres = [producto.nombre for producto in resultados]

        self.assertEqual(nombres, ["Portátil"])


if __name__ == "__main__":
    unittest.main()
