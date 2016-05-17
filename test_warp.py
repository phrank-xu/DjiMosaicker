#!/usr/local/bin/python
import unittest
from numpy.testing import assert_almost_equal
from warp import *

class WarpTests(unittest.TestCase):
    def test_getEOP(self):
        lon, lat, z, yaw, pitch, roll = getEOP('dji_0649.jpg')
        assert_almost_equal([-123.114136,38.426609,91.304548,190.422786,-0.656365,1.312138], [lon, lat, z, yaw, pitch, roll], 6)

    def test_getImage_notExist(self):
        with self.assertRaises(Exception):
            getImage("dji_0649-1.jpg")

    def test_getImage_exists(self):
        img = getImage("dji_0649.jpg")
        height, width, channels = img.shape
        self.assertEqual(height, 3000)
        self.assertEqual(width, 4000)
        self.assertEqual(channels, 3)
        self.assertEqual(img.size, 36000000)
        self.assertEqual(img.ndim, 3)

    def test_showImage(self):
        img = getImage("dji_0649.jpg")
        # showImage(img)

    def test_ll2utm(self):
        (x, y) = ll2utm(-123.114136, 38.426609)
        assert_almost_equal([490037.5, 4253156.1], [x, y], 1)

    def test_utm2ll(self):
        (lon, lat) = utm2ll(490037.5, 4253156.1)
        assert_almost_equal([-123.114136, 38.426609], [lon, lat], 6)

    def test_rotateVector(self):
        expected_rot = [
            [-0.983435068777505,  -0.180898417576039,   0.011455479783407],
            [0.181120842120780,  -0.983194253117103,   0.022897624046204],
            [0.007120817933535,   0.024593152623988,   0.999672181665555]]
        yaw, pitch, roll = 190.422786, -0.656365, 1.312138
        rot = ypr2rot(yaw, pitch, roll)
        assert_almost_equal(expected_rot, rot, 8)

    def test_img2body(self):
        x, y, z = image2body(1999.5, 1499.5)
        assert_almost_equal([0, 0, -20000], [x, y, z], 6)

        x, y, z = image2body(0, 1499.5)
        assert_almost_equal([-17302.31, 0], [x, y], 2)

        x, y, z = image2body(1999.5, 0)
        assert_almost_equal([0, 12975.66], [x, y], 2)

    def test_body2lsr(self):
        rot = ypr2rot(0, 0, 0)
        x_cam, y_cam, z_cam = image2body(0, 0)
        x_lsr, y_lsr, z_lsr = body2lsr(x_cam, y_cam, z_cam, rot)
        assert_almost_equal([-17302.31, 12975.66, -20000], [x_lsr, y_lsr, z_lsr], 2)

    def test_lsr2ground(self):
        lon_cam, lat_cam, z_cam, ground = -123.114136,38.426609,91.304548, 30

        # center
        x_lsr, y_lsr, z_lsr = -17302.31, 12975.66, -20000
        x_ll, y_ll, x_utm, y_utm = lsr2ground(x_lsr, y_lsr, z_lsr, lon_cam, lat_cam, z_cam, ground)
        assert_almost_equal([-123.114744,   38.426967], [x_ll, y_ll], 6)

        # up-middle
        x_cam, y_cam, z_cam = image2body(1999.5, 0)
        x_lsr, y_lsr, z_lsr = body2lsr(x_cam, y_cam, z_cam, ypr2rot(0, 0, 0))
        x_ll, y_ll, x_utm, y_utm = lsr2ground(x_lsr, y_lsr, z_lsr, lon_cam, lat_cam, z_cam, ground)
        assert_almost_equal([-123.113952,   38.309493], [x_ll, y_ll], 6)
        assert_almost_equal([490037.491553,  4240160.944247], [x_utm, y_utm], 6)

    def test_drawFootprints(self):
        drawFootprints([(-123.213952,   38.209493), (-123.013952,   38.209493), (-123.013952,   38.409493), (-123.213952,   38.409493)], (-123.113952,   38.309493), '649')
        # showPlot()
        pass

    def test_getFootPrints(self):
        footprints, center, title = getFootPrints('dji_0649.jpg')
        drawFootprints(footprints, center, title)

        footprints, center, title = getFootPrints('dji_0645.jpg')
        drawFootprints(footprints, center, title)
        # showPlot()

    def test_drawAllFootPrints(self):
        for i in xrange(644, 646):
            footprints, center, title = getFootPrints('dji_0%d.jpg' % i)
            drawFootprints(footprints, center, title)  
        # showPlot()
        pass

    def test_warp(self):
        warped = warp('dji_0649.jpg')
        pass 

    def test_mosaic(self):
        warped = []
        for i in xrange(644, 646):
            warped.append(warp('dji_0%d.jpg' % i))
        mosaic(warped)
        pass

if __name__ == '__main__':
    unittest.main()        