

from domain.model import allocate, OrderLine
from orm.repository import SqlRepository


@flask.route.gubbins
def allocate_endpoint():
    batches = SqlRepository.list()
    lines = [
        OrderLine(l['orderid'], l['sku'], l['qty'])
        #for l in request.params...
    ]
    allocate(lines, batches)
    session.commit()
    return 201
