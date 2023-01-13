import datetime

import pytest as pytest
from datetime import date

from domain.model import *


def make_batch_and_line(sku, batch_qty, line_qty):
    return(
        Batch('batch-001', sku, batch_qty, eta=date.today()),
        OrderLine('order-123', sku,line_qty)
    )

def test_allocating_to_a_batch_reduces_available_quantity():
    batch = Batch("batch-001", "SMALL-TABLE", qty=Quantity(20), eta=date.today())
    line = OrderLine('order-ref', 'SMALL-TABLE', Quantity(2))

    batch.allocate(line)

    assert batch.available_quantity == 18


def test_can_allocate_if_available_greater_than_required():
    large_batch, small_line = make_batch_and_line('ELEGANT-LAMP', 20, 2)
    assert large_batch.can_allocate(small_line)


def test_cannot_allocate_if_available_smaller_than_required():
    small_bacth, large_line = make_batch_and_line('ELEGANT-LAMP', 2, 20)
    assert small_bacth.can_allocate(large_line) is False


def test_can_allocate_if_available_equal_to_required():
    batch, line = make_batch_and_line('ELEGANT-LAMP', 2, 2)
    assert batch.can_allocate(line)


def test_cannot_allocate_if_skus_dont_match():
    batch = Batch(Reference('batch-001'), Sku('UNCOMFORTABLE-CHAIR'), Quantity(100), eta=None)
    different_sku_line = OrderLine(Orderid('order-123'), Sku('EXPENSIVE-TOASTER'),Quantity(10))
    assert batch.can_allocate(different_sku_line) is False


def test_can_only_deallocate_allocated_lines():
    batch,unallocated_line = make_batch_and_line('DECORATIVE-TRINKET', 20, 2)
    batch.deallocate(unallocated_line)
    assert batch._purchased_quantity == 20


def test_allocation_is_idempotent():
    batch, line = make_batch_and_line('ANGULAR-DESK', 20, 2)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_quantity == 18


def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Batch(Reference('in-stock-batch'), Sku('RETRO-CLOCK'), Quantity(100), eta=None)
    shipment_batch = Batch(Reference('shipments-batch'), Sku('RETRO-CLOCK'), Quantity(100),
                            eta=date.today() + datetime.timedelta(days=1))

    line = OrderLine(Orderid('oref'), Sku('RETRO-CLOCK'), Quantity(10))

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches():
    earliest = Batch('speedy-batch', 'MINIMALIST-SPOON', 100, eta=date.today())
    medium = Batch('normal-batch', 'MINIMALIST-SPOON', 100, eta=date.today() + datetime.timedelta(days=1))
    latest = Batch('slow-batch', 'MINIMALIST-SPOON', 100, eta=date.today() + datetime.timedelta(days=42))

    line = OrderLine('order1', 'MINIMALIST-SPOON', 10)

    allocate(line, [medium, earliest, latest])

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


def test_returns_allocated_batch_ref():
    in_stock_batch = Batch('in-stock-batch-ref', 'HIGHBROW-POSTER', 100, eta=None)
    shipment_batch = Batch('shipments-batch-ref', 'HIGHBROW-POSTER', 100, eta=date.today() + datetime.timedelta(days=1))

    line = OrderLine('oref', 'HIGHBROW-POSTER', 10)

    allocation = allocate(line, [in_stock_batch, shipment_batch])

    assert allocation == in_stock_batch.reference


def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch(Reference('batch1'), Sku('SMALL-FORK'), Quantity(10), eta=date.today())
    allocate(OrderLine(Orderid('order1'), Sku('SMALL-FORK'), Quantity(10)), [batch])

    with pytest.raises(OutOfStock, match='SMALL-FORK'):
        allocate(OrderLine(Orderid('order2'), Sku('SMALL-FORK'), Quantity(1)), [batch])
