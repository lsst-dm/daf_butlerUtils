from __future__ import print_function, division, absolute_import

import os
import numpy as np

from lsst.skymap import DiscreteSkyMap

from .base import IntField, StrField
from .common import VisitUnit, SensorUnit, CameraUnit, AbstractFilterUnit, PhysicalFilterUnit
from .backend import SqliteBackend
from .repodb import RepoDatabase
from .datasets import Dataset
from . import common

__all__ = ("makeRepoDatabase", "Coadd")

DATA_DIR = os.path.join(os.path.split(__file__)[0], "..", "..", "..", "..", "..", "tests", "data")


class HscVisitUnit(VisitUnit):
    number = IntField()
    pointing = IntField()
    field = StrField()


class HscSensorUnit(SensorUnit):
    number = IntField()


class HscCameraUnit(CameraUnit):

    def register(self, repodb):
        # Add custom visit and sensor unit classes
        repodb.registerUnitClass(HscVisitUnit)
        repodb.registerUnitClass(HscSensorUnit)
        # Add physical filters, associating them we globally-defined abstract filters.
        graph = repodb.makeGraph(UnitClasses=(AbstractFilterUnit,))
        for abstract in graph.units[AbstractFilterUnit]:
            if abstract.name in "grizy":
                physical = PhysicalFilterUnit(name="HSC-%s" % abstract.name.upper(),
                                              abstract=abstract, camera=self)
                repodb.insertUnit(physical)
        # Add sensors.
        for n in range(104):
            sensor = HscSensorUnit(number=n, camera=self)
            repodb.insertUnit(sensor)


HSC = HscCameraUnit(name="HSC")


DISCRETE_2 = DiscreteSkyMap(
    config=DiscreteSkyMap.ConfigClass(
        raList=[40.0, 15.0],
        decList=[60.0, 26.0],
        radiusList=[0.3, 0.3]
    )
)

Coadd = Dataset.subclass(
    "Coadd",
    tract=common.TractUnit,
    patch=common.PatchUnit,
    filter=common.AbstractFilterUnit
)


def makeRepoDatabase(filename=":memory:"):
    backend = SqliteBackend(filename)
    db = RepoDatabase(backend)
    db.create()
    for b in "ugrizy":
        db.insertUnit(AbstractFilterUnit(name=b))
    db.addCamera(HSC)
    db.addSkyMap(DISCRETE_2, "DISCRETE_2")
    db.addTracts("DISCRETE_2")
    db.registerDatasetType(Coadd)
    graph = db.makeGraph(FutureDatasets=[Coadd])
    for filterUnit in graph.units[common.AbstractFilterUnit]:
        if filterUnit.name != "r":
            continue
        for tractUnit in graph.units[common.TractUnit]:
            for patchUnit in graph.units[common.PatchUnit]:
                db.addDataset(Coadd(filter=filterUnit, tract=tractUnit,
                                    patch=patchUnit))
    return db
