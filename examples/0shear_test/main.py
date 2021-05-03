# INPUTS
##########
 # to store the grid data (so we dont have to keep rechecking the DIC file )
directory = r'D:\\0STUFF_IN_USE\\pyDIC\\examples\\0shear_test\\0.5cm_5-1-2021_pngs\\'
out_dir = r'D:\\0STUFF_IN_USE\\pyDIC\\examples\\0shear_test\\0.5cm_5-1-2021_pngs\\'
read_images = True           #If false, then the DIC file will be used (which stores the positional data  )
get_data_from_pickle = True#If false, then the (strains/disps will be calculated from the DIC file )
show_plots = False
save_plots = True
save_field_plots = True
grp_size_x = 8
grp_size_y = 3
correl_wind_size = (40,40) # default(80,80) # the size in pixel of the correlation windows smaller vals seem to be better at tracking 
correl_grid_size = (20,20) # the size in pixel of the interval (dx,dy) of the correlation grid
slide_y_loc = 1019
left_side_tape_x_loc = 237
pix_per_mm = 38.7

'''
    If using spyder type in the console 
    %matplotlib qt
        when you want graphs in a separate window and
    %matplotlib inline
        when you want an inline plot
'''
##########


'''
directory structure should be:
/pydic
    /examples
        /<example_name>
            -main.py
            /img
            /fig_outputs
'''





from matplotlib import pyplot as plt
import numpy as np
from scipy import stats
import os
import cv2
import gc # garbage collection to prevent the memory from piling up 
import matplotlib as mympl
import pickle as pickle
import imp
pydic = imp.load_source('pydic', '../../pydic.py')
if not show_plots: mympl.use('Agg')
import copy 







if(read_images): 
    get_data_from_pickle = False
    pydic.init(directory+r'*.png', correl_wind_size, correl_grid_size, str(directory+r'pydic.dic'))

'''
    If not reading images, then the DIC file may be read, 
   alternatively the precomputed (picked) data can be read. 
'''
if get_data_from_pickle :
    with open(directory+r'/grid_list.pkl', 'rb') as input:
        pydic.grid_list = pickle.load(input)
else:
    pydic.read_dic_file(directory+r'pydic.dic', interpolation='spline', save_image=True, strain_type="2nd_order")

if not get_data_from_pickle:
    with open(directory+'grid_list.pkl', 'wb') as output:
        pickle.dump(pydic.grid_list, output, pickle.HIGHEST_PROTOCOL)





print("Making directories for outputs in ", out_dir, "/fig_outputs")
def make_dir(the_dir):
    if not os.path.exists(the_dir):
        os.mkdir(the_dir)

make_dir(out_dir+"/fig_outputs")
make_dir(out_dir+"/fig_outputs/disp_x")
make_dir(out_dir+"/fig_outputs/disp_y")
make_dir(out_dir+"/fig_outputs/strain_xx")
make_dir(out_dir+"/fig_outputs/strain_yy")
make_dir(out_dir+"/fig_outputs/strain_xy")



def pydic_get_field(element):
    oup = [] # (objnum, x, y )
    for i in range(len(pydic.grid_list)):
        row = getattr(pydic.grid_list[i],element)
        oup.append(row)
    return np.array(oup)


# These are 3d arrays in the form (num_images, x, y )
loc_x_list      = pydic_get_field("grid_x")
loc_y_list      = pydic_get_field("grid_y")
size_x_list     = pydic_get_field("size_x")
size_y_list     = pydic_get_field("size_y")
disp_x_list     = pydic_get_field("disp_x")
disp_y_list     = pydic_get_field("disp_y") 
strain_xx_list  = pydic_get_field("strain_xx")
strain_yy_list  = pydic_get_field("strain_yy")
strain_xy_list  = pydic_get_field("strain_xy")


"""
    Make the y origin at the edge of the glass slide 
    Then scale things to the actuall mm measurements instead of pixels 
"""

loc_x_list /= pix_per_mm
loc_y_list /= pix_per_mm
disp_x_list /= pix_per_mm
disp_y_list /= pix_per_mm
for i in range(0, len(loc_y_list)):
    loc_y_list[i] -= slide_y_loc/pix_per_mm
    loc_x_list[i] -= left_side_tape_x_loc/pix_per_mm
    



""" 
    This averages the 1st axis of a array into subgroups 
"""

def avg_arr(arr, groupsize):
    i = 0 
    sum_ = np.full_like(arr[0],0)
    n_in_group = 0
    avgs = []
    for x in range(0,len(arr)):
        n_in_group += 1
        sum_ += arr[x]
        if( n_in_group == groupsize or x == len(arr)-1):
            avg = sum_/n_in_group
            sum_ = np.full_like(arr[0],0)
            avgs.append(avg)
            n_in_group = 0
    return np.array(avgs)


print("Averaging the results over width (x) ")
# These are 2d arrays in the form (y , n_imge)
loc_y_list__avgd_x     = avg_arr(np.mean(loc_y_list, 1).T, grp_size_y)
disp_x_list__avgd_x    = avg_arr(np.mean(disp_x_list, 1).T, grp_size_y)
disp_y_list__avgd_x    = avg_arr(np.mean(disp_y_list, 1).T, grp_size_y)
strain_xx_list__avgd_x = avg_arr(np.mean(strain_xx_list, 1).T, grp_size_y)
strain_yy_list__avgd_x = avg_arr(np.mean(strain_yy_list, 1).T, grp_size_y)
strain_xy_list__avgd_x = avg_arr(np.mean(strain_xy_list, 1).T, grp_size_y)



print("Averaging the results over length (y) ")
# These are 2d arrays in the form (x, n_imge)
loc_x_list__avgd_y     = avg_arr(np.mean(loc_x_list, 2).T, grp_size_x)
disp_x_list__avgd_y    = avg_arr(np.mean(disp_x_list, 2).T, grp_size_x)
disp_y_list__avgd_y    = avg_arr(np.mean(disp_y_list, 2).T, grp_size_x)
strain_xx_list__avgd_y = avg_arr(np.mean(strain_xx_list, 2).T, grp_size_x)
strain_yy_list__avgd_y = avg_arr(np.mean(strain_yy_list, 2).T, grp_size_x)
strain_xy_list__avgd_y = avg_arr(np.mean(strain_xy_list, 2).T, grp_size_x)



# Lets plot these over Time (Each axis will have its own curve)
def plot_arr(arr, plot_title, save_loc, avged_axis):
    
    
    plt.title(plot_title)
    for x_or_y in range(0, len(arr)):
        if avged_axis == "x":
            plt.plot(arr[x_or_y], label="y {:0.1f}".format(loc_y_list__avgd_x[x_or_y][0]))
        elif avged_axis == "y":
            plt.plot(arr[x_or_y], label="x {:0.1f}".format(loc_x_list__avgd_y[x_or_y][0]))
        else:
            print("ERROR in plot_arr INCORRECT AXIS ")
        plt.legend()
    if show_plots: plt.show()
    if save_plots: plt.savefig(save_loc)
    plt.clf()


plot_arr(disp_x_list__avgd_x, "disp_x avged over x", str(out_dir+"fig_outputs/disp_x_list__avgd_x"), "x")
plot_arr(disp_y_list__avgd_x, "disp_y avged over x", str(out_dir+"fig_outputs/disp_y_list__avgd_x"), "x")
plot_arr(strain_xx_list__avgd_x, "strain_xx avged over x", str(out_dir+"fig_outputs/strain_xx_list__avgd_x"), "x")
plot_arr(strain_yy_list__avgd_x, "strain_yy avged over x", str(out_dir+"fig_outputs/strain_yy_list__avgd_x"), "x")
plot_arr(strain_xy_list__avgd_x, "strain_xy avged over x", str(out_dir+"fig_outputs/strain_xy_list__avgd_x"), "x")

plot_arr(disp_x_list__avgd_y, "disp_x avged over y", str(out_dir+"fig_outputs/disp_x_list__avgd_y") ,"y")
plot_arr(disp_y_list__avgd_y, "disp_y avged over y", str(out_dir+"fig_outputs/disp_y_list__avgd_y") ,"y")
plot_arr(strain_xx_list__avgd_y, "strain_xx avged over y", str(out_dir+"fig_outputs/strain_xx_list__avgd_y") ,"y")
plot_arr(strain_yy_list__avgd_y, "strain_yy avged over y", str(out_dir+"fig_outputs/strain_yy_list__avgd_y") ,"y")
plot_arr(strain_xy_list__avgd_y, "strain_xy avged over y", str(out_dir+"fig_outputs/strain_xy_list__avgd_y") ,"y")




if(save_field_plots):
    for i in range(0, len(pydic.grid_list)):
          grid = pydic.grid_list[i]
          print("Plotting " + str(grid.image))
        
          fig = grid.plot_field(grid.disp_x, 'x disp')  
          plt.savefig(str(out_dir+"fig_outputs/disp_x/x_disp_"+str(i)))

          fig = grid.plot_field(grid.disp_y, 'y disp')
          plt.savefig(str(out_dir+"fig_outputs/disp_y/y_disp_"+str(i)))

          fig = grid.plot_field(grid.strain_xx, 'strain_xx')
          plt.savefig(str(out_dir+"fig_outputs/strain_xx/strain_xx_"+str(i)))

          fig = grid.plot_field(grid.strain_yy, 'strain_yy')
          plt.savefig(str(out_dir+"fig_outputs/strain_yy/strain_yy_"+str(i)))

          fig = grid.plot_field(grid.strain_xy, 'strain_xy')
          plt.savefig(str(out_dir+"fig_outputs/strain_xy/strain_xy_"+str(i)))
          
          plt.cla() 
          plt.clf() 
          plt.close('all')   
          



