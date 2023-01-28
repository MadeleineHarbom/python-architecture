import os

import pytest
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session, registry

from sqlalchemy_utils import database_exists, create_database

from domain.model import Batch, Reference, Sku, Quantity
from orm import repository
from orm.tables import metadata


@pytest.fixture
def in_memory_db():
    #SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///'
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SQLALCHEMY_DATABASE_URI = os.path.join(BASE_DIR, "sqlite:///batches")
    engine = create_engine(SQLALCHEMY_DATABASE_URI)
    if not database_exists(engine.url):
        create_database(engine.url)

    print(database_exists(engine.url))
    return engine


@pytest.fixture
def session(in_memory_db):
    '''
    connection = sessionmaker(bind=in_memory_db)()
    metadata.bind = in_memory_db
    print('SETUP')
    metadata.create_all()
    '''
    engine = create_engine("sqlite:///:memory:", echo=True, future=True)
    session = Session(engine)
    registry().metadata.create_all(engine)
    #yield connection
    yield session
    print('teardown')


def insert_order_line(session):
    session.execute(
        "INSERT INTO order_lines (orderid, sku, qty)"
        ' VALUES ("order1", "GENERIC-SOFA", 12)'
    )
    [[orderline_id]] = session.execute(
        "SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku",
        dict(orderid="order1", sku="GENERIC-SOFA")
    )
    return orderline_id


def insert_batch(session, batch_id):
    session.execute(
        "INSERT INTO batches (id, reference, sku, eta)"
        f" VALUES (\"{batch_id}\","
    )


def insert_allocation(session, orderline_id, batch1_id):
    raise NotImplementedError


def test_repository_exists(session):
    batch1 = Batch(Reference('batch1'), Sku('RUSTY-SOAPDISH'), Quantity(100), eta=None)
    batch2 = Batch(Reference('batch2'), Sku('DIRTY-SOAPDISH'), Quantity(55), eta=None)
    batch3 = Batch(Reference('batch3'), Sku('UNICORN-SOAPDISH'), Quantity(5), eta=None)
    print(session.bind)
    repo = repository.FakeRepository([batch1])
    print(repo)
    repo.add(batch2)
    session.commit()
    batches = repo.get_all()
    #repo.add(batch3)
    #.commit()
    rows = session.execute(
        'SELECT * FROM batches'
    )
    test = session.all()
    print(list(rows))
    print(test)

    assert True is True


def test_repository_can_save_batch(session):
    batch = Batch(Reference('batch1'), Sku('RUSTY-SOAPDISH'), Quantity(100), eta=None)

    repo = repository.FakeRepository([batch])
    repo.add(batch)
    session.commit()

    rows = session.execute(
        'SELECT reference, sku, _purchased_quantity, eta FROM batches'
    )

    assert list(rows) == ['batch1', 'RUSTY-SOAPDISH', 100, None]


def test_repository_can_retrieve_a_batch_with_alliocations(session):
    orderline_id = insert_order_line(session)
    batch1_id = insert_batch(session, 'batch1')
    insert_batch(session, 'batch2')
    insert_allocation(session, orderline_id, batch1_id)

    repo = repository.SqlRepository(session)
    retrieved = repo.get('batch1')

    expected = Batch(Reference('batch1'), Sku('GENERIC-SOFA'), Quantity(100), eta=None)
    assert retrieved == expected
    '''assert retrieved.sku == expected.sku
    assert retrieved._purchased_quantity == expected._purchased_quantity
    assert retrieved._allocatiions == {
        OrderLine(Orderid('order1'), Sku('GENERIC-SOFA'), Quantity(12))
    }'''
