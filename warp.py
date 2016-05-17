#!/usr/local/bin/python

import cv2
from math import sin, cos, tan, asin, acos, atan2, fabs, sqrt
import matplotlib.pyplot as plt
import numpy as np
import os
from pyproj import Proj, transform

# constants to be changed
IMAGE_PATH = './image/'
ORTHO_PATH = './ortho/'
MOSAIC_PATH = './mosaic/'
EPSG_GEOGRAPHIC = 4326
EPSG_UTM_10N = 32610                # location of Goat Rock Beach
PHO_WIDTH, PHO_HEIGHT = 36, 24      # 35mm film (36mm * 24mm)
IMG_WIDTH, IMG_HEIGHT = 4000, 3000  # DJI image, 35mm? impossible!
FOCAL = 20                          # 20mm
GROUND = 0                         # elevation measured from SRTM
EOPS = {
    'dji_0644.jpg' : [-123.114661,38.426805,90.689292,9.367337,1.260910,0.385252],
    'dji_0645.jpg' : [-123.114650,38.426831,90.825989,85.055542,-0.336052,1.667057],
    'dji_0646.jpg' : [-123.114429,38.426830,91.088004,88.858391,-0.070967,1.876991],
    'dji_0647.jpg' : [-123.114125,38.426831,91.091265,88.269956,0.671020,1.849037],
    'dji_0648.jpg' : [-123.114104,38.426832,90.747063,184.433167,-1.492852,1.134858],
    'dji_0649.jpg' : [-123.114136,38.426609,91.304548,190.422786,-0.656365,1.312138],
    'dji_0650.jpg' : [-123.114203,38.426195,91.007241,190.053859,0.363708,1.444969],
    'dji_0651.jpg' : [-123.114271,38.425813,91.538639,190.037347,1.106723,1.521566],
    'dji_0652.jpg' : [-123.114284,38.425752,90.900331,190.344637,1.424554,1.632872],
    'dji_0653.jpg' : [-123.114268,38.425751,90.622088,89.052669,1.243665,-1.090830],
    'dji_0654.jpg' : [-123.113839,38.425752,91.235595,88.392906,1.794960,-0.221090],
    'dji_0655.jpg' : [-123.113745,38.425749,90.437221,87.186642,1.947206,0.394757],
    'dji_0656.jpg' : [-123.113734,38.425779,90.163445,6.838638,0.624994,-0.674300],
    'dji_0657.jpg' : [-123.113662,38.426160,91.160272,6.815734,0.945930,0.550999],
    'dji_0658.jpg' : [-123.113591,38.426581,91.454023,8.740611,1.059218,1.088282],
    'dji_0659.jpg' : [-123.113556,38.426807,91.221973,9.253228,1.353285,1.449262],
    'dji_0660.jpg' : [-123.113544,38.426829,90.324952,146.612422,-1.948292,0.194904],
    'dji_0661.jpg' : [-123.113439,38.426665,90.864808,155.415639,-0.917097,1.375369],
    'dji_0662.jpg' : [-123.113183,38.426287,91.956351,155.074334,0.208305,2.160615],
    'dji_0663.jpg' : [-123.113116,38.426189,90.561950,153.763228,0.793427,2.490934],
    'dji_0664.jpg' : [-123.113115,38.426165,90.604094,187.491139,-0.312975,2.836182],
    'dji_0665.jpg' : [-123.113176,38.425826,91.781148,188.845376,0.574889,3.010090],
    'dji_0666.jpg' : [-123.113185,38.425756,91.069673,189.163989,0.764728,2.785707],
    'dji_0667.jpg' : [-123.113198,38.425754,90.750004,301.431548,-2.034127,0.511803]
}

# access functions
def getEOP(name):
    if name not in EOPS:
        raise Exception('EOP not exist: ' + name)
    lon, lat, z, yaw, pitch, roll = EOPS[name]
    return lon, lat, z, yaw, pitch, roll

def getImage(name):
    image_file = IMAGE_PATH + name
    if not os.path.exists(image_file):
        raise Exception('NOT exist: ' + image_file)
    img = cv2.imread(image_file, cv2.CV_LOAD_IMAGE_COLOR)
    return img

# utility functions
def ll2utm(lon, lat, from_epsj = EPSG_GEOGRAPHIC, to_epsj = EPSG_UTM_10N):
    epsj_ll = Proj(init='epsg:%d' % from_epsj)
    epsj_utm = Proj(init='epsg:%d' % to_epsj)
    (x, y) = transform(epsj_ll, epsj_utm, lon, lat)
    return x, y

def utm2ll(x, y, from_epsj = EPSG_UTM_10N, to_epsj = EPSG_GEOGRAPHIC):
    epsj_ll = Proj(init='epsg:%d' % from_epsj)
    epsj_utm = Proj(init='epsg:%d' % to_epsj)
    (lon, lat) = transform(epsj_ll, epsj_utm, x, y)
    return lon, lat

def ypr2rot(yaw, pitch, roll):
    s_r, c_r = sin(np.deg2rad(roll)) , cos(np.deg2rad(roll))
    s_p, c_p = sin(np.deg2rad(pitch)), cos(np.deg2rad(pitch))
    s_y, c_y = sin(np.deg2rad(yaw))  , cos(np.deg2rad(yaw))
    rot = np.matrix([
        [c_y*c_p               ,  s_y*c_p              , -s_p    ],
        [-s_y*c_r + c_y*s_p*s_r,  c_y*c_r + s_y*s_p*s_r,  c_p*s_r],
        [ s_y*s_r + c_y*s_p*c_r, -c_y*s_r + s_y*s_p*c_r,  c_p*c_r]])
    return rot

# image transformation functions
def image2body(x_img, y_img):
    # the aspect ratio specified is wrong, so use diagnoal instead
    scale = sqrt(PHO_WIDTH * PHO_WIDTH + PHO_HEIGHT * PHO_HEIGHT) * 1000 / sqrt(IMG_WIDTH * IMG_WIDTH + IMG_HEIGHT * IMG_HEIGHT)  # pixel -> micro

    x_center, y_center = float(IMG_WIDTH - 1) / 2, float(IMG_HEIGHT - 1) / 2
    x = (x_img - x_center) * scale
    y = - (y_img - y_center) * scale
    return (x, y, -FOCAL * 1000)

def body2lsr(x_body, y_body, z_body, rot):
    xyz = rot * np.matrix([x_body, y_body, z_body]).T
    x_lsr, y_lsr, z_lsr = xyz.item(0), xyz.item(1), xyz.item(2)
    return x_lsr, y_lsr, z_lsr

def lsr2ground(x_lsr, y_lsr, z_lsr, lon_cam, lat_cam, z_cam, ground):
    scale = (ground - z_cam) / z_lsr;
    x_cam_utm, y_cam_utm = ll2utm(lon_cam, lat_cam)
    x_utm = x_cam_utm + x_lsr * scale
    y_utm = y_cam_utm + y_lsr * scale
    x_ll, y_ll = utm2ll(x_utm, y_utm)
    return x_ll, y_ll, x_utm, y_utm

# footprint validation and drawing functions
def getFootPrints(name):
    img = getImage(name)
    height, width, channels = img.shape
    lon_cam, lat_cam, z_cam, yaw, pitch, roll = getEOP(name)
    
    corners = [(0, 0), (width-1, 0), (width-1, height-1), (0, height-1)]
    footprints = []
    for c in corners:
        x_body, y_body, z_body = image2body(c[0], c[1])
        x_lsr, y_lsr, z_lsr = body2lsr(x_body, y_body, z_body, ypr2rot(yaw, pitch, roll))
        x_ll, y_ll, x_utm, y_utm = lsr2ground(x_lsr, y_lsr, z_lsr, lon_cam, lat_cam, z_cam, GROUND)
        footprints.append((x_ll, y_ll, x_utm, y_utm, c[0], c[1]))

    title = name.split('.')[0]
    if len(title.split('_')) > 1:
        title = title.split('_')[1]
    return footprints, (lon_cam, lat_cam), title

def drawFootprints(corners, center, title):
    xs, ys = [], []
    for c in corners:
        xs.append(c[0])
        ys.append(c[1])
    xs.append(xs[0])
    ys.append(ys[0])

    plt.plot(xs, ys, '-^')
    plt.plot(center[0], center[1], 's')
    for i in xrange(len(corners)):
        plt.text(corners[i][0], corners[i][1], '%d' % i)
    plt.text(center[0], center[1], title)
   
def showPlot():
    plt.axis('equal')
    plt.show()

def showImage(img):
    cv2.imshow('image',img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# warp and mosaic functions
def warp(name):
    print 'warping %s ... ' % name
    
    src = '%s%s' % (IMAGE_PATH, name)
    translated = '%s%s-translate.tif' % (ORTHO_PATH, name.split('.')[0])
    warped = '%s%s-warp.tif' % (ORTHO_PATH, name.split('.')[0])

    if not os.path.exists(src):
        raise Exception('NOT exist: ' + src)
    if os.path.exists(translated):
        # print 'removing %s ...' % translated
        os.unlink(translated)
    if os.path.exists(warped):
        # print 'removing %s ...' % warped
        os.unlink(warped)

    footprints, center, title = getFootPrints(name)
    cmd = '/usr/local/bin/gdal_translate '
    for f in footprints:
        cmd += '-gcp %.1f %.1f %.10f %.10f ' % (f[4], f[5], f[2], f[3])
    cmd += '"%s" ' % src
    cmd += '"%s" ' % translated
    cmd += ' | 2>&1'
    os.system(cmd)

    cmd = '/usr/local/bin/gdalwarp -r bilinear "%s" "%s" | 2>&1' % (translated, warped)
    os.system(cmd)

    return os.path.basename(warped)
    
def mosaic(warped):
    mosaiked = '%sdji-mosaic.tif' % MOSAIC_PATH
    if os.path.exists(mosaiked):
        # print 'removing %s ...' % mosaiked
        os.unlink(mosaiked)

    cmd = '/usr/local/bin/gdal_merge.py -o "%s" -n 0 ' % mosaiked
    for w in warped:
        ortho = '%s%s' % (ORTHO_PATH, w)
        if not os.path.exists(ortho):
            raise Exception('NOT exist: ' + ortho)
        cmd += '"%s" ' % ortho
    # cmd += ' | 2>&1'
    print 'cmd: ' + cmd
    os.system(cmd)
    return mosaiked

if __name__ == '__main__':
    warped = []
    for i in xrange(644, 667):
       warped.append(warp('dji_0%d.jpg' % i))

    print 'mosaicking ...' 
    mosaiked = mosaic(warped)

    # showImage(cv2.imread(mosaiked, cv2.CV_LOAD_IMAGE_COLOR))

