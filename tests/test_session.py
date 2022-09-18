import pytest
from opd.session import Session


@pytest.fixture
def session():
    return Session(
        filename="metadata.json",
    )


def test_type_check(session):
    assert isinstance(session, Session)


def test_class_load_check(session):
    assert len(session.data) == 1579
    assert str(session.min_time) == "2022-03-23T00:00:00.066667"
    assert str(session.max_time) == "2022-03-23T00:01:45.266667"


def test_detect_forklifts_and_people(session):
    forklifts, people = session.detect_forklifts_and_people(337)

    assert len(forklifts) == 2
    assert len(people) == 1


def test_get_distances(session):
    d = session.get_distances(337)

    assert len(d) == 2
    d = session.get_distances(337, 2)
    assert len(d) == 2


def test_data_frame(session):
    df = session.stat_table
    assert len(set(df["obj2_type"])) == 2
    assert len(set(df["obj1_type"])) == 2
    assert df.shape[1] == 12
