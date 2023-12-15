global pm, disk
import sys

pm = [0]*524288
disk = [[0 for i in range(1024)] for j in range(512)]
free_frames = [0]*1024
free_frames[0] = 1
free_frames[1] = 1

def st_init(szf):
    global pm
    i = 0
    #print(szf)
    while i < len(szf):
        pm[2*szf[i]] = szf[i+1]
        pm[2*szf[i]+1] = szf[i+2]
        free_frames[szf[i+2]] = 1
        i += 3

def pt_init(szf):
    global pm
    i = 0
    while i < len(szf):
        if pm[2*szf[i]+1] < 0:
            disk[abs(pm[2*szf[i]+1])][szf[i+1]] = szf[i+2]
        else:
            pm[pm[2*szf[i]+1]*512+szf[i+1]] = szf[i+2]
            free_frames[szf[i+2]] = 1
        i += 3

def read_block(b, m):
    global pm, disk
    i = 0
    for elem in disk[b]:
        pm[m+i] = elem
        i += 1

def pa_from_va(va):
    global pm, disk
    for address in va:
        s = address >> 18
        p = (address >> 9) & 511
        w = address & 511
        pw = address & 262143
        if pw >= pm[2*s]:
            print(-1, end = " ")
            continue
        if pm[2*s+1] < 0:
            f1 = 0
            while free_frames[f1]:
                f1 += 1
            free_frames[f1] = 1
            read_block(abs(pm[2*s+1]), f1*512)
            pm[2*s+1] = f1
        if pm[pm[2*s+1]*512+p] < 0:
            f2 = 0
            while free_frames[f2]:
                f2 += 1
            free_frames[f2] = 1
            read_block(abs(pm[pm[2*s+1]*512+p]), f2*512)
            pm[pm[2*s+1]*512+p] = f2
        print(pm[pm[2*s+1]*512+p]*512+w, end = " ")

if __name__=='__main__':
    filename = input("Enter init file name: ")
    f = open(filename, 'r')
    text = f.readlines()
    st_init([eval(i) for i in text[0].split()])
    pt_init([eval(i) for i in text[1].split()])
    #print(pm[16], pm[17], pm[1541])

    filename = input("Enter input file name: ")
    f = open(filename, 'r')
    text = f.readlines()
    stdout = sys.stdout
    sys.stdout = open('output.txt', 'w')
    pa_from_va([eval(i) for i in text[0].split()])
    sys.stdout.close()
    sys.stdout = stdout