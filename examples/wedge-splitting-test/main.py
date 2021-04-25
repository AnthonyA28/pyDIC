#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of pydic, a free digital correlation suite for computaing strain fields
#
# Author :  - Damien ANDRE, SPCTS/ENSIL-ENSCI, Limoges France
#             <damien.andre@unilim.fr>
#
# Copyright (C) 2017 Damien ANDRE
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



# ====== INTRODUCTION
# The wedge splitting test shows how to use pydic module with the deep_flow
# option. This option allows to get the full displacement field. It is
# very usefull for detecting crack path. The proposed example highlight this
# feature with the wedge splitting test.
#
# Note that :
#  - pictures of the wedge splitting test are located in the 'img' directory
#  - deep flow is quiet long... please be patient

import numpy as np
import cv2
import sys
import math
import glob
from matplotlib import pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
import cv2
from scipy.interpolate import griddata
from scipy.interpolate import Rbf
import scipy.interpolate
import copy
import os

# locate the pydic module and import it
import imp
pydic = imp.load_source('pydic', '../../pydic.py')



#  ====== RUN PYDIC TO COMPUTE DISPLACEMENT AND STRAIN FIELDS (STRUCTURED GRID)
correl_wind_size = (2,2) # the size in pixel of the correlation windows
correl_grid_size = (1,1) # the size in pixel of the interval (dx,dy) of the correlation grid




pydic.init('./img/essai*.BMP', correl_wind_size, correl_grid_size, "result.dic", deep_flow=True)


# and read the result file for computing strain and displacement field from the result file
# note that with the deep_flow DIC, it's better to not use any interpolation
pydic.read_dic_file('result.dic', interpolation='raw', strain_type='cauchy', save_image=True, scale_disp=10, scale_grid=25)


# now we display for each image the displacement field in a HSV format where :
# - color highlights displacement direction,
# - saturation highlights displacement intensity.

for grid in pydic.grid_list[1:]:
    grid.draw_disp_hsv_img(save_img=False, show_img=True)





