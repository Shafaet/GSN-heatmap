'''
findfast.py :   In this program a fast search algorithm findclosest() is developped to be used in gomsurveyplot.py
using the python bisect module

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
    this source code; if not, see <https://www.gnu.org/licenses/gpl.html>


'''

import bisect

a = [-20,-10,30,40,50,60]

x = -11
print 'search for', x

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
    
    print 'bi', i
    
    li = None
    
    if (i-1 < 0):
        lval = amin
        li = 0
    else:
        lval = a[i-1]
        li = i-1
        
    print 'lval' ,lval
    
    if (i == len(a)):
        rval = a[i-1]
        ri = i-1
    else:
        rval = a[i]
        ri = i
        
    print 'ravl', rval
    
    if (x - lval) <= (rval - x):
        return li
    else:
        return ri

i = findclosest (a,x);
print 'i', i
print 'a[i]', a[i]

    
