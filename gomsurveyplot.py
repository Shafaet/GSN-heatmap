'''
    gomsurveyplot.py:   This program creates the sky heatmap plot from the GomSpace survey data. 
    
    input:         A CSV file containing the sky survey data generated by the survey program provided by GomSpace.
    output:        A heatmap plot of the input data. 
                   In the plot the elevation are tagged from 0 to 9 where 0 means 90 degree elevation and 9 means 0 degre elevation.
                   And all the middle values can be understood similarly. For tag value t the degree value of the elevation is (9-t)*10.  
                   Please consult the documentation to understand the mathematical basis of this plot.                   
     
    Usages:        To use the program run: python gomsurveyplot.py [inputfile name]
                   Replace [inputfile name] with our csv file names. 
    
    Prerequisites: This program is tested for python2.7 
                   You need the following libraries
                   
                   numpy     
                   Scipy
                   matplotlib 
                   
                   To install them on Debian or Ubuntu run:
                        
                        sudo apt-get install python-numpy python-scipy python-matplotlib 

                   Alternatively you can also use pip to install them. Please look up the internet for pip instructions.
                   
    
    Note:          some auxiliary files are created in the process of crating the final heat-map. They are a legacy of the development process. 
                   If you dont need or understand them then you can safely ignore them. 
    
    Copyright (C) 2016 Tanvirul Islam, National University
                         of Singapore <tanvirulbd@gmail.com>

    This source code is free software; you can redistribute it and/or
    modify it under the terms of the GNU Public License as published 
    by the Free Software Foundation; either version 3 of the License,
    or (at your option) any later version.

    This source code is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    Please refer to the GNU Public License for more details.

    You should have received a copy of the GNU Public License along with
    this source code; if not, see: <https://www.gnu.org/licenses/gpl.html>
'''


import os
import sys
import inspect 
import csv
import re
import numpy as np

import bisect

import math
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from scipy import ndimage


'''
    function:   findclosest() uses bisection algorithm to find 
                the closest element in a sorted list. 
    inputs: a  = a list sorted in an ascending order 
            x  = the search item
            
    output: i = the index of the value closest to x in a
'''
def findclosest(a,x):
    '''
        a must be a sorted list in an ascending order
    '''
    
    amin = a[0]
    amax = a[-1]
    
    i = bisect.bisect(a,x)
        
    li = None
    
    if (i-1 < 0):
        lval = amin
        li = 0
    else:
        lval = a[i-1]
        li = i-1
       
    
    if (i == len(a)):
        rval = a[i-1]
        ri = i-1
    else:
        rval = a[i]
        ri = i
    
    if (x - lval) <= (rval - x):
        return li
    else:
        return ri




'''
The main function
'''
if __name__ == "__main__":
 
 
    '''
        Take the inputfile name from the commandline
    '''
    infile = ""
    if len(sys.argv) >1:
        infile = sys.argv[1]
    else:
        print "Error: Wrong parameters!"
        print "try: python gomsurveyplot.py infile.csv"
        exit()
        
    #rval = float(sys.argv[2])
    #tval = float(sys.argv[3])
    
    
#GomSpace csv data to be loaded in polar format in this list
polar_data = []

with open(infile, 'r') as fp:
    lines = fp.readlines()
    
    
    #Read the input file; tokenize it and load it in the data list. 
    
    data = []
    for ln in lines:
        line_toks = re.split(",|\r\n",ln)
        data.append(line_toks)
    print len(lines)
    print len(data)
    
    
    # convert all the elevation angle to radious where radious r means (9-r)*10 degree elevation
    for r in reversed (range (1,10)):
        for i in range(0,36):
            polar_data.append( [r,
                float(data[(9-r)*36+i][0]),
                float(data[(9-r)*36+i][2])])
    
    #take the avg of all the 90 degree elevation readings
    sum90 = 0
    for i in range(0,36):
            sum90 += float(data[(9)*36+i][2])
    avg90 = sum90 / 36.0
    
    polar_data.append([0,0,avg90])
    
    #print polar_data size
    print len(polar_data)
    
    #print the polar data to csv file 
    outfile3 = "d3"+"polar"+infile
    with open (outfile3, 'w') as f_eos:
        w = csv.writer(f_eos)
        w.writerows(sorted(polar_data))
        print "output written in "+ "d3"+"polar"+infile


''' 
    The data is taken for only 360 points. To get the 2d heatmap for the whole sky
    we want to interpolate it for all the other points.  
    We cannot perform interpolation using the existing python interpolation libraries if the 
    data is in polar format. There fore first we convert the polar data to Cartesian format.
    
'''


cart_data = []
with open(outfile3, 'r') as fp:
    lines = fp.readlines()
    data = []
    for ln in lines:
        line_toks = re.split(",|\r\n",ln)
        r = float(line_toks[0])
        theta = float(line_toks[1])
        val = float(line_toks[2])
        x = r * math.cos(math.radians(theta))
        y = r * math.sin(math.radians(theta))
        
        cart_data.append([x,y,val])
        
    #print Cartesian data to file 
    outfile4 = "d4"+"cart-sparce" + outfile3
    with open (outfile4, 'w') as f_eos:
        w = csv.writer(f_eos)
        w.writerows(sorted(cart_data))
        #print "output written in "+"d4"+"cart-sparce"+infile
        

'''
    Now we read the suvey data in curtesian format and perform a bicubic interpolation. 
'''

points = []
values = []
infile =outfile4
with open(infile, 'r') as fp:
    lines = fp.readlines()
    data = []
    for ln in lines:
        line_toks = re.split(",|\r\n",ln)
        points.append( [float(line_toks[0]),float(line_toks[1])])
        values.append(float(line_toks[2]))
    
    #print points.shape
    #print values.shape
    
    npoints = np.array(points)
    print npoints.shape
    nvalues = np.array(values)
    print nvalues.shape
    print 'minimum value=',min(nvalues)
    #points to be interpolated
    in_points = []
    
    #take equally spaced 1000 values on the x line between -9 to 9
    ixp = np.linspace(-9,9,1000)
    iyp = np.linspace(-9,9,1000) # same for the y
    
    # now we creat 1000*1000 meshgrids for x and y values of the target points. 
    # on which the interpolated values are to be computed. 
    # the shape of the meshgrid has some quirks please carefully review the numpy.meshgrid documentation.
    xv, yv = np.meshgrid(ixp, iyp)
    print xv.shape 
    print 'shape up'

    #interpolated values
    # the survey points and values are given in npoints and nvalues. The fill values are initially given to be minimum of all values. 
    # the interpolated values are returned in invals.     
    invals = griddata(npoints,nvalues,(xv,yv),method='cubic',fill_value=min(nvalues))
       
    
    #the polar points where we would sample from the interpolated data. 
    #we have taken 1000*1000 cartesian grid for interpolation to minimize rounding error in this sampling. 
r = np.linspace(0,9,100)
t = np.linspace(0.0, 2.0 * np.pi, 360)
    
    
# as usual, creat the meshgrid. 
rv,tv = np.meshgrid(r, t)
print rv.shape
print tv.shape
print 'shape rv'

#print rv
#print tv

#initialize with zeros
polar_values = np.zeros(rv.shape,dtype=np.float)

for i in range(rv.shape[0]): #shape is a pair object
    for j in range(rv.shape[1]):
        '''
            for each polar point
                find the (x,y) value of the point
                find the closest point in the interpolated values and take that to be the value of 
                the original polar point. 
                (we can exponentially improve the speed by usign binary search here)
        '''
        x_dist = rv[i][j]*np.cos(tv[i][j])
        
        x_loc =  min(range(len(ixp)), key=lambda i: abs(ixp[i]-x_dist))
        #x_loc = findclosest(ixp,x_dist)
        y_dist = rv[i][j]*np.sin(tv[i][j])
        y_loc =  min(range(len(iyp)), key=lambda i: abs(iyp[i]-y_dist))
        #y_loc = findclosest(iyp, y_dist)
        
        #the sampling happends here
        polar_values[i][j] = invals[y_loc][x_loc]
   
   
print polar_values.shape

#plt.title('MD1 noise-floor heatmap')

# GridSpec is used to format the heatmap plot
#here 2 side by side plot space are created.
gs = gridspec.GridSpec(1, 2,
                       width_ratios=[10,1],
                       )

#ax1 contains the polar heatmap
ax1 = plt.subplot(gs[0], projection="polar", aspect=1.)
ax1.set_theta_zero_location("N")
ax1.title.set_text('noise-floor heatmap')


#ax1.set_theta_direction(-1) #make it clockwise

#ax1.set_theta_offset(np.pi/2.0)

#ax2 contains the colour-value chart / colorbar.
ax2 = plt.subplot(gs[1])
ax2.title.set_text('noise level in dbm')

#Create a polar projection
#ax1 = plt.subplot(projection="polar")
#ax1 = plt.subplot(111)

'''anything below or above vmin or vmax respectively will be replaced
    by vmin or vmax respectively '''
# the colorbar is returned in im 
im = ax1.pcolormesh(tv,rv,polar_values,vmin=-125,vmax=-90)

# If you dont want a fixed max - min range use the following instead
#im = ax1.pcolormesh(tv,rv,polar_values)

ax1.grid(True)
plt.colorbar(im, cax=ax2) #plot the colorbor bside the heatmap


plt.savefig("processed"+infile+".png") # save to file. other image formats are available. just change the suffics here. 
print "output plot to file "+"processed"+infile+".png"
plt.show() #display plot. 



