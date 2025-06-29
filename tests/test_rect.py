from math import pi

import pytest


@pytest.mark.parametrize(
    "width, height, center, rotation, expected_points",
    [
        (10, 5, (0, 0, 0), 0, [(5, -2.5, 0), (5, 2.5, 0), (-5, 2.5, 0), (-5, -2.5, 0)]),
        (10, 5, (1, 1, 0), 0, [(6, -1.5, 0), (6, 3.5, 0), (-4, 3.5, 0), (-4, -1.5, 0)]),
        (10, 5, (0, 0, 0), pi / 2, [(-2.5, -5, 0), (2.5, -5, 0), (2.5, 5, 0), (-2.5, 5, 0)]),
        (10, 5, (1, 1, 0), pi / 2, [(-1.5, -4, 0), (3.5, -4, 0), (3.5, 6, 0), (-1.5, 6, 0)]),
    ],
)
def test_create_rect(width, height, center, rotation, expected_points):
    from pyrx import Db, Ge

    from pyrx_sample_project.rect import create_rectangle

    rect = create_rectangle(width, height, center, rotation)

    assert isinstance(rect, Db.Polyline)
    result_points = rect.toPoint3dList()
    assert len(result_points) == 4

    assert len(expected_points) == 4
    for point in expected_points:
        p = Ge.Point3d(*point)
        for result_point in result_points:
            if result_point.isEqualTo(p):
                break
        else:
            pytest.fail(f"Expected point {point} not found in {result_points}.")
