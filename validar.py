import re
import requests


def ValidaCnpj(cnpj: str) -> str | None:
    if not isinstance(cnpj, str):
        return None

    if not cnpj:
        return None

    cnpj = cnpj.replace(" ", "").replace(".", "").replace("/", "").replace("-", "")

    if len(cnpj) != 14:
        return None

    if not cnpj.isnumeric():
        return None

    return cnpj


def validaEmail(email):
    regex = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    if regex.match(email):
        return True
    return False


def validaCep(cep: str) -> str | None:
    if not isinstance(cep, str):
        return None
    if not cep:
        return None

    cep = cep.replace(" ", "").replace("-", "").replace(".", "")

    if len(cep) != 8:
        return None

    if not cep.isnumeric():
        return None

    resp = requests.get(f"https://viacep.com.br/ws/{cep}/json/")

    if "erro" in resp.json():
        return None

    return cep
