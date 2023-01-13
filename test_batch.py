from datetime import date

from domain.model import OrderLine, Batch, Reference, Quantity, Orderid, Sku


def make_batch_and_line(sku, batch_qty, line_qty):
    return(
        Batch(Reference('batch-001'), Sku(sku), Quantity(batch_qty), eta=date.today()),
        OrderLine(Orderid('order-123'), Sku(sku),Quantity(line_qty))
    )


def test_allocating_to_a_batch_reduces_available_quantity():
    batch = Batch(Reference("batch-001"), Sku("SMALL-TABLE"), qty=Quantity(20), eta=date.today())
    line = OrderLine(Orderid('order-ref'), Sku('SMALL-TABLE'), Quantity(2))
    batch.allocate(line)
    assert batch.available_quantity == 18


def test_can_allocate_if_available_greater_than_required():
    large_batch, small_line = make_batch_and_line('ELEGANT-LAMP', 20, 2)
    assert large_batch.can_allocate(small_line)


def test_cannot_allocate_if_available_smaller_than_required():
    small_batch, large_line = make_batch_and_line('ELEGANT-LAMP', 2, 20)
    assert small_batch.can_allocate(large_line) is False


def test_can_allocate_if_available_equal_to_required():
    batch, line = make_batch_and_line('ELEGANT-LAMP', 2, 2)
    assert batch.can_allocate(line)


def test_cannot_allocate_if_skus_dont_match():
    batch = Batch(Reference('batch-001'), Sku('UNCOMFORTABLE-CHAIR'), Quantity(100), eta=None)
    different_sku_line = OrderLine(Orderid('order-123'), Sku('EXPENSIVE-TOASTER'), Quantity(10))
    assert batch.can_allocate(different_sku_line) is False


def test_allocation_is_idempotent():
    batch, line = make_batch_and_line('ANGULAR-DESK', 20, 2)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_quantity == 18


def test_can_only_deallocate_allocated_lines():
    batch,unallocated_line = make_batch_and_line('DECORATIVE-TRINKET', 20, 2)
    batch.deallocate(unallocated_line)
    assert batch._purchased_quantity == 20

