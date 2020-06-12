# This file is part of obs_base.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (http://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from lsst.daf.butler import Butler
from ..utils import getInstrument


def registerInstrument(repo, instrument):
    """Add an instrument to the data repository.

    Parameters
    ----------
    repo : `str`
        URI to the location to create the repo.
    instrument : `list` [`str`]
        The fully-qualified name of an Instrument subclass.

    Raises
    ------
    RuntimeError
        If the instrument can not be imported, instantiated, or obtained from
        the registry.
    TypeError
        If the instrument is not a subclass of lsst.obs.base.Instrument.
    """
    butler = Butler(repo, writeable=True)
    for instr in instrument:
        instrInstance = getInstrument(instr, butler.registry)
        instrInstance.register(butler.registry)
