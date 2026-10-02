import pytest
from shop import Order, OrderService, CONFIG, PaymentGateway


@pytest.fixture
def productos():
    return [
        {"name": "Teclado", "price": 800, "quantity": 1},
        {"name": "Mouse", "price": 300, "quantity": 1},
    ]


# CP-01: monkeypatch.setattr -> sustituir el servicio de pagos (RF-10, RF-11, RF-14)
def test_cp01_setattr_pago_simulado(monkeypatch, productos):
    def fake_charge(self, amount):
        return {"status": "approved", "amount": amount}

    monkeypatch.setattr(PaymentGateway, "charge", fake_charge)

    service = OrderService(CONFIG)
    resultado = service.process_order(Order(productos))

    assert resultado["payment"]["status"] == "approved"
    assert resultado["payment"]["amount"] == pytest.approx(1148.4)
    assert resultado["order"]["total"] == pytest.approx(1148.4)


# CP-02: monkeypatch.setitem -> cambiar la tasa de impuesto en CONFIG (RF-07, RF-08, RF-09)
def test_cp02_setitem_tasa_impuesto(monkeypatch, productos):
    monkeypatch.setitem(CONFIG, "tax_rate", 0.08)

    service = OrderService(CONFIG)
    resultado = service.calculate_total(Order(productos))

    assert resultado["subtotal"] == 1100
    assert resultado["discount"] == pytest.approx(110)
    assert resultado["tax"] == pytest.approx(79.2)
    assert resultado["total"] == pytest.approx(1069.2)


# CP-03: monkeypatch.delattr -> servicio de descuentos no disponible (RF-12, RF-13)
def test_cp03_delattr_sin_descuento(monkeypatch, productos):
    service = OrderService(CONFIG)
    monkeypatch.delattr(service, "discount_service")

    resultado = service.calculate_total(Order(productos))

    assert resultado["subtotal"] == 1100
    assert resultado["discount"] == 0
    assert resultado["tax"] == pytest.approx(176)
    assert resultado["total"] == pytest.approx(1276)
