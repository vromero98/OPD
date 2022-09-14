import pytest
from opd.detection import Detection

@pytest.fixture
def detection():
    return Detection(
        id="123",
        detection_class="forklift",
        frame=1,
        timestamp="2022-01-01T00:00:00",
        x=0,
        y=0,
    )


def test_type_check(detection):
    assert isinstance(detection, Detection)


def test_types(detection):
    assert detection.id == "123"
    assert detection.detection_class in {"forklift", "person"}
    assert isinstance(detection.X, list)
    assert isinstance(detection.Y, list)
    assert isinstance(detection.Vx, list)
    assert isinstance(detection.Vy, list)

def test_add_frame(detection):
    detection.add_frame(frame = 2, ts ="2022-01-01T00:00:01", x = 0, y = 1)
    assert len(detection.frames) == 2
    assert detection.Vy == [0.0, 1.0]
    assert detection.Vx == [0.0, 0.0]
    assert len(detection.X) == 2
    assert len(detection.Y) == 2
    assert detection.frames[-1] == 2

def test_get_coord(detection):
    # because length of the default one is 1 the we return None object
    assert detection.get_coord(1) == (0,0)
    detection.add_frame(frame = 2, ts ="2022-01-01T00:00:01", x = 0, y = 1)
    assert detection.get_coord(2) == (0,1)
    assert detection.get_coord(1) == (0,0)

def test_get_speed(detection):
    # because length of the default one is 1 the we return None object
    assert detection.get_speed(1) == (0,0)
    detection.add_frame(frame = 2, ts ="2022-01-01T00:00:01", x = 0, y = 1)
    assert detection.get_speed(2) == (0,1)
    assert detection.get_speed(1) == (0,0)


def test_get_coord_projection(detection):
    # because length of the default one is 1 the we return None object
    assert detection.get_coord_projection(1) == (0,0)
    detection.add_frame(frame = 2, ts ="2022-01-01T00:00:01", x = 0, y = 1)
    assert detection.get_coord(2) == (0,1)
    assert detection.get_coord_projection(2,1) == (0,2)

def test_get_future_location(detection):
    # because length of the default one is 1 the we return None object
    assert detection.get_future_location() == (0,0)
    detection.add_frame(frame = 2, ts ="2022-01-01T00:00:01", x = 0, y = 1)
    assert detection.get_future_location() == (0,1)
    assert detection.get_future_location(1) == (0,2)
