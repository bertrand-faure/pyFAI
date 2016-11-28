#!/usr/bin/env python
# coding: utf-8
#
#    Project: Azimuthal integration
#             https://github.com/pyFAI/pyFAI
#
#    Copyright (C) 2015 European Synchrotron Radiation Facility, Grenoble, France
#
#    Principal author:       Jérôme Kieffer (Jerome.Kieffer@ESRF.eu)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import absolute_import, division, print_function

__doc__ = "test suite for polarization corrections"
__author__ = "Jérôme Kieffer"
__contact__ = "Jerome.Kieffer@ESRF.eu"
__license__ = "MIT"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
__date__ = "28/11/2016"


import unittest
import numpy
from .utilstest import getLogger
logger = getLogger(__file__)
from ..azimuthalIntegrator import AzimuthalIntegrator


class TestPolarization(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.shape = (13, 13)
        Y, X = numpy.ogrid[-6:7, -6:7]
        self.rotY = numpy.radians(30.0 * Y)
        self.rotX = numpy.radians(30.0 * X)
        self.tth = numpy.sqrt(self.rotY ** 2 + self.rotX ** 2)
        chi = numpy.arctan2(self.rotY, self.rotX)
        self.ai = AzimuthalIntegrator(dist=1, pixel1=0.1, pixel2=0.1)
        self.ai._cached_array["2th_center"] = self.tth
        self.ai._cached_array["chi_center"] = chi

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.shape = self.rotY = self.rotX = self.tth = self.ai = None

    def testNoPol(self):
        "without polarization correction should be 1"
        self.assertTrue(abs(self.ai.polarization(factor=None) - numpy.ones(self.shape)).max() == 0, "without polarization correction should be 1")

    def testCircularPol(self):
        "Circular polarization should decay in (1+(cos2θ)^2)/2"
        pol = (1.0 + numpy.cos(self.tth) ** 2) / 2.0
        self.assertTrue(abs(self.ai.polarization(factor=0) - pol).max() == 0, "with circular polarization correction is independent of chi")
        self.assertTrue(abs(self.ai.polarization(factor=0, axis_offset=1) - pol).max() == 0, "with circular polarization correction is independent of chi")

    def testHorizPol(self):
        "horizontal polarization should decay in (cos2θ)**2 in horizontal plane and no correction in vertical one"
        self.assertTrue(abs(self.ai.polarization(factor=1)[:, 6] - numpy.ones(13)).max() == 0, "No correction in the vertical plane")
        self.assertTrue(abs(self.ai.polarization(factor=1)[6] - numpy.cos(self.rotX) ** 2).max() < 1e-15, "cos(2th)^2 like in the horizontal plane")

    def testVertPol(self):
        "Vertical polarization should decay in (cos2θ)**2 in vertical plane and no correction in horizontal one"
        self.assertTrue(abs(self.ai.polarization(factor=-1)[6] - numpy.ones(13)).max() == 0, "No correction in the horizontal plane")
        self.assertTrue(abs(self.ai.polarization(factor=-1)[:, 6] - (numpy.cos((2 * self.rotX)) + 1) / 2).max() < 1e-15, "cos(2th)^2 like in the verical plane")

    def testoffsetPol(self):
        "test for the rotation of the polarization axis"
        self.assertTrue(abs(self.ai.polarization(factor=1, axis_offset=numpy.pi / 2)[6] - numpy.ones(13)).max() == 0, "No correction in the horizontal plane")
        self.assertTrue(abs(self.ai.polarization(factor=1, axis_offset=numpy.pi / 2)[:, 6] - (numpy.cos((2 * self.rotX)) + 1) / 2).max() < 1e-15, "cos(2th)^2 like in the verical plane")


def suite():
    testsuite = unittest.TestSuite()
    testsuite.addTest(TestPolarization("testNoPol"))
    testsuite.addTest(TestPolarization("testCircularPol"))
    testsuite.addTest(TestPolarization("testHorizPol"))
    testsuite.addTest(TestPolarization("testVertPol"))
    testsuite.addTest(TestPolarization("testoffsetPol"))
    # testsuite.addTest(TestPolarization("test2th"))
    return testsuite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
