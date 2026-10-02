"""Domain enumerations for real estate transactions, property categories, and cities."""

from enum import IntEnum


class TransactionType(IntEnum):
    """Transaction purpose: rental or sale."""

    ALUGUEL = 1
    VENDA = 2


class PropertyType(IntEnum):
    """Known property categories on the Vera Imobiliária platform."""

    TODOS = 0
    APARTAMENTO = 1
    LOJA = 2
    CASA = 3
    LOTE = 4
    GALPAO = 5
    SALA = 6
    SITIO = 7
    FAZENDA = 8
    CHACARA = 10
    QUITINETE = 11
    COBERTURA = 16
    CASA_GEMINADA = 17
    TERRENO = 18
    SALA_PREDIO = 21


class CityId(IntEnum):
    """Recognized municipalities supported by the portal."""

    TODAS = 0
    TIMOTEO = 1
    CORONEL_FABRICIANO = 2
    IPATINGA = 3
    ANTONIO_DIAS = 12
    MARLIERIA = 14
    JAGUARACU = 18
    SANTANA_DO_PARAISO = 21
    CORREGO_NOVO = 22
