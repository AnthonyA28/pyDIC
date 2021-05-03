

from matplotlib import pyplot as plt
import numpy as np
from scipy import stats
import os
import cv2
import gc # garbage collection to prevent the memory from piling up 
import matplotlib as mympl
# I think this solves the fail to allocate bitmap issue 
#   WARNING: only for use for saving images (not showing them )

import pickle as pickle

# INPUTS
##########
 # to store the grid data (so we dont have to keep rechecking the DIC file )
directory = r'test_images2/'
# directory = r'D:\AA_GD\Documents\UT\Research\Results\DIC\lessimages/')
read_images = True          #If false, then the DIC file will be used (which stores the positional data  )
get_data_from_pickle = False #If false, then the (strains/disps will be calculated from the DIC file )
show_plots = False
save_plots = True
save_field_plots = True
group_size = 8
##########


if( not show_plots):
    mympl.use('Agg')


import imp
pydic = imp.load_source('pydic', '../../pydic.py')

'''
directory structure should be:
/pydic
    /examples
        /<example_name>
            -main.py
            /img
            /fig_outputs


'''




if(read_images):
    get_data_from_pickle = False


if(read_images):
    correl_wind_size = (80,80)# default(80,80) # the size in pixel of the correlation windows
    correl_grid_size = (20,20) # the size in pixel of the interval (dx,dy) of the correlation grid
    pydic.init(directory+r'*.jpg', correl_wind_size, correl_grid_size, str(directory+r'pydic.dic'))

if( get_data_from_pickle ):
    with open(directory+r'/grid_list.pkl', 'rb') as input:
        pydic.grid_list = pickle.load(input)
else:
    pydic.read_dic_file(directory+r'pydic.dic', interpolation='spline', save_image=True, strain_type="2nd_order")

obj = pydic

if( not get_data_from_pickle):
    with open(directory+'grid_list.pkl', 'wb') as output:
        pickle.dump(pydic.grid_list, output, pickle.HIGHEST_PROTOCOL)




def attribute_to_matrix(obj, element):
    oup = [] # (objnum, x, y )
    for i in range(len(obj)):
        row = getattr(obj[i],element)
        oup.append(row)
    return np.array(oup)

def attribute_to_matrix_avged(obj, element, axis):

    oup = [] # (objnum, x, y )
    for i in range(len(obj)):
        row = np.mean(getattr(obj[i],element), axis)
        oup.append(row)
    return np.array(oup)


def avg_over_y(grid_obj, groupsize):
    print("grouping Ys by "+str(groupsize))
    i = 0 
    sum_ = np.full_like(grid_obj[0],0)
    out = []
    for g_i in range(len(grid_obj)):
        n_in_group = 0
        sum_ = np.full_like(grid_obj[g_i][0],0)
        disp_avgs = []
        for x in range(0,len(grid_obj[g_i])):
            n_in_group += 1
            sum_ += grid_obj[g_i][x]
            if( n_in_group == groupsize or x == len(grid_obj[g_i])-1):
                avg = sum_/n_in_group
                sum_ = np.full_like(grid_obj[g_i][0],0)
                disp_avgs.append(avg)
                n_in_group = 0
        out.append(disp_avgs)
    return np.array(out)

def avg_arr_over_y(arr, groupsize):
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


disp_y = attribute_to_matrix(pydic.grid_list, "disp_y")

print(str(disp_y.shape) + "  (num imgs, x_grids, y_grids)")
print(str(disp_y.T.shape) + "  (y_grids, x_grids, num imgs)")

disp_y = attribute_to_matrix_avged(pydic.grid_list, "disp_y",0)
print(str(disp_y.shape) + "  (num imgs, y_grids)")
disp_y = avg_over_y(disp_y, group_size)
print(str(disp_y.shape) + "  (num imgs, s y_grids)")



grid_list_disps = [] # holds a matrix of my calculated absolut displacements 
pos_names_mat = []
for grid in pydic.grid_list:
    # print("calculating disp for  " + str(grid.image)) 
    index = 0 
    pos_names = []
    pos_avgs = []
    # arr = [grid.image]
    grid_disps = []
    for i in range(grid.size_x):
        arr_y = []
        for j in range(grid.size_y):
            disp = grid.correlated_point[index] - grid.reference_point[index]
            abs_disp = np.sqrt(disp[0]**2 + disp[1]**2)
            arr_y.append(abs_disp)
            pos_names.append(str(grid.grid_x[i,j])                   + ',' + str(grid.grid_y[i,j]))
            index = index + 1
        grid_disps.append(arr_y)
    # print("\n\n")
    grid_disps = np.array(grid_disps)
    grid_list_disps.append(grid_disps)
    pos_names_mat.append(pos_names)
grid_list_disps = np.array(grid_list_disps)
# mat = np.array(mat).T # now is is (y,x)







# pos_names_mat = np.array(pos_names_mat).T

avged_grids = []

for i in range(0, len(grid_list_disps)):
    avged_x = np.mean(grid_list_disps[i],0)
    avged_grids.append(avged_x)
    # print(grid_list_disps[i])

avged_grids = avg_over_y(avged_grids, group_size)


dir_path = os.getcwd()
x = os.walk(dir_path)
print("Making dirs in ", str(dir_path+"/fig_outputs"))
if not os.path.exists(str(dir_path+"/fig_outputs")):
    os.mkdir(str(dir_path+"/fig_outputs"))
if not os.path.exists(str(dir_path+"/fig_outputs/aa_disps")):
    os.mkdir(str(dir_path+"/fig_outputs/aa_disps"))
if not os.path.exists(str(dir_path+"/fig_outputs/x_disps")):
    os.mkdir(str(dir_path+"/fig_outputs/x_disps"))
if not os.path.exists(str(dir_path+"/fig_outputs/y_disps")):
    os.mkdir(str(dir_path+"/fig_outputs/y_disps"))
if not os.path.exists(str(dir_path+"/fig_outputs/strain_xx")):
    os.mkdir(str(dir_path+"/fig_outputs/strain_xx"))
if not os.path.exists(str(dir_path+"/fig_outputs/strain_yy")):
    os.mkdir(str(dir_path+"/fig_outputs/strain_yy"))
# except  Exception as e:
#     print("figoutput directories exist ", e)

# Need to coordinate averages 
grid_y = np.mean(attribute_to_matrix_avged(pydic.grid_list, "grid_y", 0),0)
grid_x = np.mean(attribute_to_matrix_avged(pydic.grid_list, "grid_x", 0),0)


if( save_plots or show_plots):

    # # print(grid_list_disps)
    avged_grids = np.array(avged_grids) 
    avged_grids = avged_grids.T # now transpose that 

    plt.title("avged absolut disps")
    for y in range(0, len(avged_grids)):
        plt.plot(avged_grids[y], label=str(y)+" ("+str(grid_x[y])+","+str(grid_y[y])+")")
        plt.legend()
    if show_plots:
        plt.show()
    if(save_plots):
        plt.savefig("fig_outputs/abs_disp")
    plt.clf()

grid_y = avg_arr_over_y(grid_y, group_size)
grid_x = avg_arr_over_y(grid_x, group_size)

if( save_plots or show_plots):
    disp_y = attribute_to_matrix_avged(pydic.grid_list, "disp_y", 0)
    disp_y = avg_over_y(disp_y, group_size)
    disp_y = disp_y.T
    plt.title("disp_y")
    for y in range(0, len(disp_y)):
        plt.plot(disp_y[y], label=str(str(y)+" ("+str(grid_x[y])+","+str(grid_y[y])+")"))
        plt.legend()
    if show_plots:
        plt.show()
    if(save_plots):
        plt.savefig("fig_outputs/disp_y")
    plt.clf()

if( save_plots or show_plots):
    plt.title("disp_x")
    disp_x = attribute_to_matrix_avged(pydic.grid_list, "disp_x", 0)
    disp_x = avg_over_y(disp_x, group_size)
    
    disp_x = disp_x.T
    for y in range(0, len(disp_x)):
        plt.plot(disp_x[y], label=str(y)+" ("+str(grid_x[y])+","+str(grid_y[y])+")")
        plt.legend()
    if show_plots:
        plt.show()
    if(save_plots):
        plt.savefig("fig_outputs/disp_x")
    plt.clf()

if( save_plots or show_plots):
    strain_yy = attribute_to_matrix_avged(pydic.grid_list, "strain_yy", 0)
    strain_yy = avg_over_y(strain_yy, group_size)
    strain_yy = strain_yy.T
    plt.title("strain_yy")
    for y in range(0, len(strain_yy)):
        plt.plot(strain_yy[y], label=str(y)+" ("+str(grid_x[y])+","+str(grid_y[y])+")")
        plt.legend()
    if show_plots:
        plt.show()
    if(save_plots):
        plt.savefig("fig_outputs/strain_yy")
    plt.clf()

if( save_plots or show_plots):
    strain_xx = attribute_to_matrix_avged(pydic.grid_list, "strain_xx", 0)
    strain_xx = avg_over_y(strain_xx, group_size)
    strain_xx = strain_xx.T
    plt.title("strain_xx")
    for y in range(0, len(strain_xx)):
        plt.plot(strain_xx[y], label=str(y)+" ("+str(grid_x[y])+","+str(grid_y[y])+")")
        plt.legend()
    if show_plots:
        plt.show()
    if(save_plots):
        plt.savefig("fig_outputs/strain_xx")
    plt.clf()



# DO some nice plotting 
def get_min_and_max(obj, element):
    total_min = getattr(obj[0],element).min()
    total_max = getattr(obj[0],element).max() 
    for i in range(len(obj)):
        a_max = getattr(obj[i],element).max()
        a_min = getattr(obj[i],element).min()
        if( a_max > total_max):
            total_max = a_max
        if( a_min < total_min):
            total_min = a_min
    return total_min, total_max
        



pos_names_mat = []
for grid in pydic.grid_list:
    index = 0 
    row = []
    for i in range(grid.size_x):
        col = []
        for j in range(grid.size_y):
            disp = grid.correlated_point[index] - grid.reference_point[index]
            abs_disp = np.sqrt(disp[0]**2 + disp[1]**2)
            col.append(abs_disp)
            index += 1
        row.append(col)
    grid.aa_disps = np.array(row)



total_min_disp_x, total_max_disp_x = get_min_and_max(pydic.grid_list,"disp_x")
total_min_disp_y, total_max_disp_y = get_min_and_max(pydic.grid_list,"disp_y")
total_min_aa_disp, total_max_aa_disp = get_min_and_max(pydic.grid_list,"aa_disps")

if(save_field_plots):
    for i in range(0, len(pydic.grid_list)):
          grid = pydic.grid_list[i]
          print("Plotting " + str(grid.image))
        
          fig = grid.plot_field(grid.aa_disps, 'abs disp')  
          plt.savefig("fig_outputs/aa_disps/aa_disp_"+str(i))

          fig = grid.plot_field(grid.disp_x, 'x disp')  
          plt.savefig("fig_outputs/x_disps/x_disp_"+str(i))

          fig = grid.plot_field(grid.disp_y, 'y disp')
          plt.savefig("fig_outputs/y_disps/y_disp_"+str(i))

          fig = grid.plot_field(grid.strain_xx, 'strain_xx')
          plt.savefig("fig_outputs/strain_xx/strain_xx_"+str(i))

          fig = grid.plot_field(grid.strain_yy, 'strain_yy')
          plt.savefig("fig_outputs/strain_yy/strain_yy_"+str(i))
          
          plt.cla() 
          plt.clf() 
          plt.close('all')   
          














































""" Probably nonsense 
# for grid in grid_list_disps:
#     # average the displacements over a deltaY 
#     groups = 5 

#     num_per_group = int(np.ceil(len(grid_list_disps[0])/groups))
#     new_grid = []
#     strin = ""
#     x = 0 
#     end = False
#     while not end:
#         group = []
#         summed = np.zeros(len(grid[0]))
#         num_in_this_group = 0
#         for sg in range(0, num_per_group):
#             summed += grid[int(x+sg)]
#             num_in_this_group += 1
#             strin += str(int(x+sg)) + ", "
#             if (x + sg >= len(grid[0]) ):
#                 end = True
#                 break
#         summed/= num_in_this_group
#         new_grid.append(summed)
#         strin += "\n\n\n"
#         x += num_per_group 

# new_grid = np.array(new_grid)
# print(strin)

# r = 0 
# new_grid = new_grid.T
# for grid in new_grid:

#     plt.plot(row)
#     print(pos_names_mat[r])
#     plt.show()
#     r += 1
#     # for col in row:
#         # print(col)
#         # plt.savefig("col[-0]")
"""














# def worker(rang):
#   print("working")
#   for i in rang:
#       grid = pydic.grid_list[i]
#       # grid.plot_field(grid.disp_x, 'x disp')
#       grid.plot_field(grid.disp_x, 'x disp', min_val=total_min_disp_x, max_val=total_max_disp_x)
#       plt.savefig("fig_outputs/x_disps/x_disp_"+str(i))
#       plt.cla() 
#       plt.clf() 
#       plt.close('all')   
#       gc.collect()

#       grid.plot_field(grid.disp_y, 'y disp', min_val=total_min_disp_y, max_val=total_max_disp_y)  # plt.show()
#       plt.savefig("fig_outputs/y_disps/y_disp_"+str(i))
      
#       plt.cla() 
#       plt.clf() 
#       plt.close('all')   
#       gc.collect()


    

# procs = []
# rang = len(pydic.grid_list)

# skip = 5
# for i in range(0, rang, skip):
#     row = []
#     for j in range(0, skip):
#         row.append(i + j)

#     print("creating a process for " + str(row))

#     proc=mp.Process(target=worker, args=(row))
#     # proc.daemon=True
#     proc.start()

# for proc in procs:
#     proc.join()







# grid = pydic.grid_list[-1]
# # print(grid.correlated_point)
# # print(grid.correlated_point)

# mat = []
# pos_names_mat = []
# for grid in pydic.grid_list:
#     print(grid.image)
#     index = 0 
#     arr = []
#     pos_names = []
#     # arr = [grid.image]
#     for i in range(grid.size_x):
#         for j in range(grid.size_y):
#             disp = grid.correlated_point[index] - grid.reference_point[index]
#             abs_disp = np.sqrt(disp[0]**2 + disp[1]**2)
#             arr.append(abs_disp)
#             pos_names.append(str(grid.grid_x[i,j])                   + ',' + str(grid.grid_y[i,j]))
#             # strin = str(
#                 # str(index)                              + ',' +
#                 # str(i)                                  + ',' + str(j)                  + ',' + 
#                 # str(grid.grid_x[i,j])                   + ',' + str(grid.grid_y[i,j])   + ',' + 
#                 # str(grid.correlated_point[index][0])    + ',' + str(grid.correlated_point[index][1]) + ',' + #x, y 
#                 # str(grid.reference_point[index][0])     + ',' + str(grid.correlated_point[index][1]) + ',' + #x, y 
#                 # str(abs_disp)
#             # )
#             index = index + 1
#             # print(strin)
#     mat.append(arr)
#     pos_names_mat.append(pos_names)
#     # print("\n\n")

# mat = np.array(mat).T
# pos_names_mat = np.array(pos_names_mat).T

# r = 0 
# for row in mat:

#     plt.plot(row)
#     print(pos_names_mat[r])
#     plt.show()
#     r += 1
#     # for col in row:
#         # print(col)
#         # plt.savefig("col[-0]")













# total_min_disp_x = pydic.grid_list[0]["disp_x"].min()
# total_max_disp_x = pydic.grid_list[0].disp_x.max() 
# total_min_disp_y = pydic.grid_list[0].disp_y.min()
# total_max_disp_y = pydic.grid_list[0].disp_y.max() 
# for i in range(len(pydic.grid_list)):
#     a_max_disp_x = pydic.grid_list[i].disp_x.max()
#     a_min_disp_x = pydic.grid_list[i].disp_x.min()
#     a_max_disp_y = pydic.grid_list[i].disp_y.max()
#     a_min_disp_y = pydic.grid_list[i].disp_y.min()
#     if( a_max_disp_x > total_max_disp_x):
#         total_max_disp_x = a_max_disp_x
#     if( a_max_disp_y > total_max_disp_y):
#         total_max_disp_y = a_max_disp_y
#     if( a_min_disp_x < total_min_disp_x):
#         total_min_disp_x = a_min_disp_x
#     if( a_min_disp_y < total_min_disp_y):
#         total_min_disp_y = a_min_disp_y

