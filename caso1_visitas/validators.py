# Dependencias para validar datos antes de persistirlos.
from django.core.exceptions import ValidationError

# Rango referencial del cuerpo del RUT de personas naturales.
MIN_RUT_PERSONA = 1_000_000
MAX_RUT_PERSONA = 30_000_000


# Valida nombres y apellidos formados solo por letras, sin espacios.
def validar_nombre(value):
    if not value or not value.isalpha():
        raise ValidationError("Este campo solo puede contener letras, sin espacios.")


# Calcula el dígito verificador chileno usando módulo 11.
def calcular_digito_verificador(rut):
    rut = int(rut)
    total = 0
    factor = 2

    for digit in reversed(str(rut)):
        total += int(digit) * factor
        factor = 2 if factor == 7 else factor + 1

    resto = 11 - (total % 11)
    if resto == 11:
        return "0"
    if resto == 10:
        return "K"
    return str(resto)


# Devuelve un RUT numérico con su dígito verificador.
def formatear_rut(rut):
    rut = int(rut)
    return f"{rut}-{calcular_digito_verificador(rut)}"


# Normaliza, valida el formato, rango y dígito del RUT.
def normalizar_rut(value):
    text = str(value).strip().upper().replace(".", "").replace(" ", "")
    if "-" in text:
        partes = text.split("-")
        if len(partes) != 2:
            raise ValidationError("Ingresa el RUT con el formato 12345678-5.")
        cuerpo, digito = partes
    else:
        if len(text) < 2:
            raise ValidationError("Ingresa el RUT con el formato 12345678-5.")
        cuerpo, digito = text[:-1], text[-1]

    if not cuerpo.isdigit() or digito not in "0123456789K":
        raise ValidationError("El RUT solo puede contener números, guion y K.")

    rut = int(cuerpo)
    if not MIN_RUT_PERSONA <= rut <= MAX_RUT_PERSONA:
        raise ValidationError(
            f"El cuerpo del RUT debe estar entre {MIN_RUT_PERSONA:,} "
            f"y {MAX_RUT_PERSONA:,}.".replace(",", ".")
        )

    digito_esperado = calcular_digito_verificador(rut)
    if digito != digito_esperado:
        raise ValidationError("El dígito verificador del RUT no es válido.")

    return f"{rut}-{digito_esperado}"


# Adaptador de validación para usar en los campos del modelo.
def validar_rut(value):
    normalizar_rut(value)
