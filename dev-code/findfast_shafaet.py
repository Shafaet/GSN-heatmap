import bisect
import random
def findclosest(a, x):
    '''
        a must be a sorted list in an ascending order
    '''

    amin = a[0]
    amax = a[-1]

    i = bisect.bisect(a, x)

    li = None

    if (i - 1 < 0):
        lval = amin
        li = 0
    else:
        lval = a[i - 1]
        li = i - 1


    if (i == len(a)):
        rval = a[i - 1]
        ri = i - 1
    else:
        rval = a[i]
        ri = i

    if (x - lval) <= (rval - x):
        return li
    else:
        return ri

def findclosest2(a, x):
    i = bisect.bisect(a, x)
    if i == len(a):
        return len(a)-1
    if i == 0:
        return 0
    if x - a[i-1] <= a[i] - x:
        return i-1
    return i


def testcorrectness():
    a = []
    for i in range(0, 1000):
        a.append(random.uniform(500, 10000))

    a = sorted(a)

    for v in range(10000):
        v = random.uniform(0, 20000)
        res1 = findclosest(a, v)
        res2 = findclosest2(a, v)
        assert res1==res2
    print "PASSED"

testcorrectness()
