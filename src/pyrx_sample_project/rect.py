from __future__ import annotations

import collections.abc as c

from pyrx import Db, Ge


def create_rectangle(
    width: float, height: float, center: c.Iterable[float] = (0.0, 0.0, 0.0), rotation: float = 0.0
):
    w2 = width / 2.0
    h2 = height / 2.0
    points = (
        Ge.Point3d(-w2, -h2, 0.0),
        Ge.Point3d(w2, -h2, 0.0),
        Ge.Point3d(w2, h2, 0.0),
        Ge.Point3d(-w2, h2, 0.0),
    )
    mt = Ge.Matrix3d.translation(Ge.Vector3d(tuple(center)))
    mr = Ge.Matrix3d.rotation(rotation, Ge.Vector3d.kZAxis, Ge.Point3d.kOrigin)
    m = mt * mr
    points_t = [m * p for p in points]
    pline = Db.Polyline(points_t)
    pline.setClosed(True)
    return pline
