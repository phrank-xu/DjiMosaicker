# DjiMosaicker
Sample python scripts to warp and mosaic 26 aerial photos of goat rock beach by a DJI FC 300X.

To run, you will need some 3rd party libraries. Use Mac as an example, following steps will be needed:

  1. opencv:
      brew tap homebrew/science, 
      brew install opencv 
  
  2. matplotlib:
      pip install matplotlib
  
  3. numpy:
      pip install numpy
  
  4. pyproj:
      download from https://pypi.python.org/pypi/pyproj?, 
      cd Downloads/pyproj-1.9.5.1, 
      python setup.py install
  
  5. gdal:
      brew install gdal
  
  6. qgis (download and install from here):
      http://www.kyngchaos.com/software/qgis

folder structure:

./image
./image/dji_0644.jpg
./image/dji_0645.jpg
./image/dji_0646.jpg
./image/dji_0647.jpg
./image/dji_0648.jpg
./image/dji_0649.jpg
./image/dji_0650.jpg
./image/dji_0651.jpg
./image/dji_0652.jpg
./image/dji_0653.jpg
./image/dji_0654.jpg
./image/dji_0655.jpg
./image/dji_0656.jpg
./image/dji_0657.jpg
./image/dji_0658.jpg
./image/dji_0659.jpg
./image/dji_0660.jpg
./image/dji_0661.jpg
./image/dji_0662.jpg
./image/dji_0663.jpg
./image/dji_0664.jpg
./image/dji_0665.jpg
./image/dji_0666.jpg
./image/dji_0667.jpg
./mosaic
./mosaic/.DS_Store
./ortho
./ortho/.DS_Store
./test_warp.py
./warp.py

After all the prerequisits are in place, make sure the unittest runs (by running './test_warp.py'). then call './warp.py' to do the job.

  
