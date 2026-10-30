from models import ProductoElectronico, ProductoRopa
from Services import TiendaService


def mostrar_productos(tienda: TiendaService) -> None:
    for producto in tienda.listar_productos():
        print(" ", producto)


def main() -> None:
    tienda = TiendaService()

    # usuarios
    ana = tienda.registrar_usuario("cliente", "Ana López", "ana@mail.com", "Calle Mayor 5, Madrid")
    luis = tienda.registrar_usuario("cliente", "Luis Pérez", "luis@mail.com", "Av. Galicia 12, Vigo")
    marta = tienda.registrar_usuario("cliente", "Marta Gil", "marta@mail.com", "C/ Alcalá 20, Madrid")
    admin = tienda.registrar_usuario("administrador", "Admin", "admin@tienda.com")

    print("=== USUARIOS ===")
    for u in [ana, luis, marta, admin]:
        print(" ", u, "| admin:", u.is_admin())

    # productos
    portatil = ProductoElectronico("Portátil", 899.99, 5, 24)
    auriculares = ProductoElectronico("Auriculares", 59.90, 20, 12)
    camiseta = ProductoRopa("Camiseta", 15.00, 30, "M", "Negro")
    pantalon = ProductoRopa("Pantalón vaquero", 39.95, 10, "42", "Azul")
    sudadera = ProductoRopa("Sudadera", 29.99, 8, "L", "Gris")

    for p in [portatil, auriculares, camiseta, pantalon, sudadera]:
        tienda.anadir_producto(p)

    print("\n=== INVENTARIO ===")
    mostrar_productos(tienda)

    # pedidos
    print("\n=== PEDIDOS ===")
    pedido1 = tienda.realizar_pedido(ana.id, {portatil.id: 1, auriculares.id: 2})
    print(pedido1, "\n")
    pedido2 = tienda.realizar_pedido(luis.id, {camiseta.id: 3, pantalon.id: 1})
    print(pedido2, "\n")
    pedido3 = tienda.realizar_pedido(marta.id, {sudadera.id: 2, auriculares.id: 1})
    print(pedido3, "\n")

    # pedido que tiene que fallar por falta de stock
    try:
        tienda.realizar_pedido(ana.id, {portatil.id: 10})
    except ValueError as e:
        print("Error:", e)

    # segundo pedido de Ana para que el historico tenga mas de uno
    tienda.realizar_pedido(ana.id, {camiseta.id: 2})

    print(f"\n=== HISTÓRICO DE {ana.nombre.upper()} ===")
    for pedido in tienda.listar_pedidos_usuario(ana.id):
        print(pedido, "\n")

    print("=== STOCK ACTUALIZADO ===")
    mostrar_productos(tienda)


if __name__ == "__main__":
    main()
