"""Excepciones de la lógica de negocio.

Heredan de ValueError para que el código antiguo que hacía
`except ValueError` siga funcionando, pero permiten a la API
distinguir qué código HTTP devolver en cada caso.
"""


class RecursoNoEncontrado(ValueError):
    """El usuario, producto o pedido pedido no existe -> 404."""


class Conflicto(ValueError):
    """La operación choca con el estado actual (stock, email repetido...) -> 409."""


class OperacionNoPermitida(ValueError):
    """La operación no está permitida para ese usuario -> 403."""
