from datetime import date, timedelta

import pytest

from domain.model import Batch, Sku, Quantity, Orderid, OrderLine, Reference, allocate, OutOfStock


def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Batch(Reference('in-stock-batch'), Sku('RETRO-CLOCK'), Quantity(100), eta=None)
    shipment_batch = Batch(Reference('shipments-batch'), Sku('RETRO-CLOCK'), Quantity(100),
                           eta=date.today() + timedelta(days=1))

    line = OrderLine(Orderid('oref'), Sku('RETRO-CLOCK'), Quantity(10))

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches():
    earliest = Batch('speedy-batch', 'MINIMALIST-SPOON', 100, eta=date.today())
    medium = Batch('normal-batch', 'MINIMALIST-SPOON', 100, eta=date.today() + timedelta(days=1))
    latest = Batch('slow-batch', 'MINIMALIST-SPOON', 100, eta=date.today() + timedelta(days=42))

    line = OrderLine('order1', 'MINIMALIST-SPOON', 10)

    allocate(line, [medium, earliest, latest])

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


def test_returns_allocated_batch_ref():
    in_stock_batch = Batch('in-stock-batch-ref', 'HIGHBROW-POSTER', 100, eta=None)
    shipment_batch = Batch('shipments-batch-ref', 'HIGHBROW-POSTER', 100, eta=date.today() + timedelta(days=1))

    line = OrderLine('oref', 'HIGHBROW-POSTER', 10)

    allocation = allocate(line, [in_stock_batch, shipment_batch])

    assert allocation == in_stock_batch.reference


def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch(Reference('batch1'), Sku('SMALL-FORK'), Quantity(10), eta=date.today())
    allocate(OrderLine(Orderid('order1'), Sku('SMALL-FORK'), Quantity(10)), [batch])

    with pytest.raises(OutOfStock, match='SMALL-FORK'):
        allocate(OrderLine(Orderid('order2'), Sku('SMALL-FORK'), Quantity(1)), [batch])
