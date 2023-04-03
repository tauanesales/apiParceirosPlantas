import pytest
import validar


@pytest.mark.parametrize(
    "cnpj_in, cnpj_out",
    [
        ("01234567891234", "01234567891234"),
        (" 01234567891234", "01234567891234"),
        ("01234567891234 ", "01234567891234"),
        (" 01234567891234 ", "01234567891234"),
        ("0123456/7891234", "01234567891234"),
        ("012345678.91234", "01234567891234"),
        ("01234-567891234", "01234567891234"),
        ("01.234.567/8912-34", "01234567891234"),
        (" 01.234.567/8912-34", "01234567891234"),
        ("01.234.567/8912-34 ", "01234567891234"),
        (" 01.234.567/8912-34 ", "01234567891234"),
    ],
)
def testeValidarCnpj(cnpj_in: str, cnpj_out: str) -> None:
    """
    Teste validar.processar_cnpj retorna o cnpj correto quando um CNPJ válido é passado.
    """
    assert validar.ValidaCnpj(cnpj_in) == cnpj_out


@pytest.mark.parametrize(
    "cnpj",
    [
        "01.234.567/892-34",
        "01.234.567/8912-4",
        "0.234.567/8912-4",
        "0123456789123",
        ")!@#$%¨&*(!@#$)",
        "0123456789123456789",
        "",
        "cat",
        "dog",
        "100",
        "Meu cnpj é 01.234.567/8912-34",
    ],
)
def validaStringsInvalidosCNPJ(cnpj: str) -> None:
    """
    Teste retorna None com CNPJs do tipo string inválidos.
    """
    assert validar.ValidaCnpj(cnpj) is None


@pytest.mark.parametrize(
    "cnpj",
    [
        False,
        True,
        0,
        1,
        2,
        2.2,
        None,
    ],
)
def testeRetornaCnpjNone(cnpj: str) -> None:
    """
    Teste retorna None quando tipos diferentes são passados.
    """
    assert validar.ValidaCnpj(cnpj) is None


@pytest.mark.parametrize(
    "email",
    [
        "a@b.c",
        "tauane@inc.com",
        "tauane@gmail.com",
        "tauane@gmail.com.br",
        "tauane_sales@gmail.com.br",
        "tauane-sales@gmail.com.br",
        "tauane-sales_2@gmail.com.br",
        "tauane_3@inc.com",
    ],
)
def testeEmailsValidos(email: str) -> None:
    """
    Teste validar.email_valido retorna verdadeiro com emails válidos.
    """
    assert validar.validaEmail(email) == True


@pytest.mark.parametrize(
    "email",
    [
        "@b.c",
        "a@.c",
        "a@b.",
        "a@bc",
        "ab.c",
        "@bb.cc",
        "aa@.cc",
        "aa@bb.",
        "aa@bbcc",
        "aabb.cc",
    ],
)
def testeEmailsInvalidos(email: str) -> None:
    """
    Teste validar.email_valido retorna falso com emails inválidos.
    """
    assert validar.validaEmail(email) == False


@pytest.mark.parametrize(
    "cep_in, cep_out",
    [
        ("01001000", "01001000"),
        (" 01001000", "01001000"),
        ("01001000 ", "01001000"),
        (" 01001000 ", "01001000"),
        (" 01001.000 ", "01001000"),
        (" 01-001000 ", "01001000"),
        ("01001-000", "01001000"),
        ("01.001000", "01001000"),
        ("01.001-000", "01001000"),
        (" 01.001-000", "01001000"),
        ("01.001-000 ", "01001000"),
        (" 01.001-000 ", "01001000"),
    ],
)
def testeCepValido(cep_in: str, cep_out: str, mocker) -> None:
    """
    Teste se validar.validaCep retorna o cep correto quando um cep válido é passado.
    """

    def mock_get(*args, **kwargs):
        class MockResponse:
            def json(self):
                return {"cep": "01001000"}

        return MockResponse()

    mocker.patch("validar.requests.get", mock_get)
    assert validar.validaCep(cep_in) == cep_out


@pytest.mark.parametrize(
    "cep",
    [
        "01001-00",
        "0101-000",
        "01.234.567/8912-4",
        "0.234.567/8912-4",
        "0123456789123",
        "",
        "cat",
        "dog",
        "100",
        "Meu cep é 01001-000",
    ],
)
def testeCepComCamposInvalidos(cep: str) -> None:
    """
    Teste validar.validaCep retorna None com CEPs do tipo string inválidos.
    """
    assert validar.validaCep(cep) is None


@pytest.mark.parametrize(
    "cep",
    [
        False,
        True,
        0,
        1,
        2,
        2.2,
        None,
    ],
)
def testeCepNaoString(cep: str) -> None:
    """
    Teste validar.validaCep retorna None quando tipos diferentes são passados.
    """
    assert validar.validaCep(cep) is None


@pytest.mark.parametrize(
    "cep",
    [
        "10000000",
        "01000000",
        "00100000",
        "00010000",
        "00001000",
        "00000100",
        "00000010",
        "00000001",
    ],
)
def testeCepValidoNaoEncontrado(cep: str, mocker) -> None:
    """
    Teste validar.validaCep retorna None com CEPs válidos mas inexistentes.
    """

    def mock_get(*args, **kwargs):
        class MockResponse:
            def json(self):
                return {"erro": True}

        return MockResponse()

    mocker.patch("validar.requests.get", mock_get)
    assert validar.validaCep(cep) is None
