import flask as flask
from flask import request

from domain.model import OrderLine, allocate, Batch


@flask.route.gubbins
def allocate_endpoint():
    session = start_session()

    # extract order line from request
    line = OrderLine(
        request.json['orderid'],
        request.json['sku'],
        request.json['quy']
    )

    # lead all batches from the DB
    batches = session.query(Batch).all()

    # call domain service
    allocate(line, batches)

    # save the allocation back to the database
    session.commit()

    return 201
