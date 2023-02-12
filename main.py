from collections import deque

global pcb, rcb, rl, current_processes

def init():
    global pcb, rcb, rl, current_processes
    pcb = [{'state':None, 'parent':None, 'priority':None, 'children':deque(), 'resources':deque()} for i in range(16)]
    rcb = [dict.fromkeys(['state', 'inventory', 'waitlist']) for i in range(4)]
    rcb[0]['inventory'] = 1
    rcb[0]['state'] = 1
    rcb[0]['waitlist'] = deque()
    for i in range(1,4):
        rcb[i]['state'] = i
        rcb[i]['inventory'] = i
        rcb[i]['waitlist'] = deque()
    rl = [deque() for i in range(3)]
    pcb[0]['state'] = 0
    pcb[0]['priority'] = 0
    rl[0].append(0)
    current_processes = 1
    print('\n', end="")
    scheduler()

def create(p):
    global pcb, rcb, rl, current_processes
    if p not in range(3):
        # print('Error: invalid priority')
        print(-1, end="")
        return
    if current_processes >= 16:
        # print('Error: no free processes')
        print(-1, end="")
        return
    current_process = (rl[2] + rl[1] + rl[0])[0]
    j = 0
    while(pcb[j]['state'] != None):
        j+=1
    pcb[j]['state'] = 0
    pcb[current_process]['children'].append(j)
    pcb[j]['parent'] = current_process
    pcb[j]['priority'] = p
    rl[p].append(j)
    # print('process %s created' % j)
    current_processes += 1
    scheduler()

def destroy(j):
    global pcb, rcb, rl, current_processes
    current_process = (rl[2] + rl[1] + rl[0])[0]
    j = int(j)
    # print(type(j), pcb[current_process]['children'], type(current_process))
    if j not in pcb[current_process]['children'] and j != current_process:
        # print('Error: cannot destroy process not in scope')
        print(-1, end="")
        return
    processes_destroyed = destroy_helper(j)
    # print('%s processes destroyed' % processes_destroyed)
    current_processes -= processes_destroyed
    scheduler()

def destroy_helper(j):
    global pcb, rcb, rl
    processes_destroyed = 0
    children_tbd = pcb[j]['children'].copy()
    for i in children_tbd:
        processes_destroyed += destroy_helper(i)
    if pcb[j]['parent']:
        pcb[pcb[j]['parent']]['children'].remove(j)
    for p in rl:
        if j in p:
            p.remove(j)
    for r in rcb:
        if r in r['waitlist']:
            r['waitlist'].remove(j)
    process_resources = pcb[j]['resources']
    for resource, units in process_resources:
        rcb[resource]['state'] += units
        # if not rcb[r]['waitlist']:
        #     rcb[r]['state'] = 0
        for wl_process, req_units in rcb[resource]['waitlist']:
            if req_units <= rcb[resource]['state']:
                rl[pcb[wl_process]['priority']].append(wl_process)
                pcb[wl_process]['resources'].append([resource, req_units])
                rcb[resource]['state'] -= req_units
            else:
                break
        # if not rcb[r]['waitlist']:
        #     rcb[r]['state'] = 0
        # else:
        #     wl_process = rcb[r]['waitlist'].popleft()
        #     rl[pcb[wl_process]['priority']].append(j)
        #     pcb[wl_process]['resources'].append(r)
    pcb[j] = {'state':None, 'parent':None, 'priority':None, 'children':deque(), 'resources':deque()}
    return processes_destroyed + 1

def request(r, k):
    global pcb, rcb, rl
    # print(range(len(rcb)))
    if r not in range(len(rcb)):
        # print('Error: resource does not exist')
        print(-1, end="")
        return
    # if k > rcb[r]['inventory']:
    #     print(-1, end="")
    #     return
    current_process = (rl[2] + rl[1] + rl[0])[0]
    # if r in [rk[0] for rk in pcb[current_process]['resources']]:
    #     # print('Error: resource already allocated')
    #     print(-1, end="")
    #     return
    # print(rcb[r], k)
    if rcb[r]['state'] >= k:
        rcb[r]['state'] -= k
        if r in [rk[0] for rk in pcb[current_process]['resources']]:
            resource_index = [rk[0] for rk in pcb[current_process]['resources']].index(r)
            pcb[current_process]['resources'][resource_index][1] += k
        else:
            pcb[current_process]['resources'].append([r,k])
        # print('resource %s allocated %s units' % (r, k))
    else:
        pcb[current_process]['state'] = 1
        for p in rl:
            if current_process in p:
                p.remove(current_process)
        rcb[r]['waitlist'].append([current_process, k])
        # print('process %s blocked' % current_process)
    scheduler()
    

def release(r,k):
    global pcb, rcb, rl
    current_process = (rl[2] + rl[1] + rl[0])[0]
    if r not in [rk[0] for rk in pcb[current_process]['resources']]:
        # print('Error: cannot release unallocated resource')
        print(-1, end="")
        return
    resource_index = [rk[0] for rk in pcb[current_process]['resources']].index(r)
    if k > pcb[current_process]['resources'][resource_index][1]:
        # print('Error: cannot release more resources than currently held')
        print(-1, end="")
        return
    pcb[current_process]['resources'][resource_index][1] -= k
    if pcb[current_process]['resources'][resource_index][1] == 0:
        del pcb[current_process]['resources'][resource_index]
    rcb[r]['state'] += k
    # if not rcb[r]['waitlist']:
    #     rcb[r]['state'] = 0
    for wl_process, req_units in rcb[r]['waitlist']:
        if req_units <= rcb[r]['state']:
            rl[pcb[wl_process]['priority']].append(wl_process)
            pcb[wl_process]['resources'].append([r, req_units])
            rcb[r]['state'] -= req_units
        else:
            break
        # j = rcb[r]['waitlist'].popleft()
        # j_index = j[0]
        # j_k = j[1]
        # rl[pcb[j_index]['priority']].append(j_index)
        # pcb[j_index]['resources'].append((r, j_k))
    # print('resource %s released' % r)
    scheduler()

def timeout():
    global rl
    process_list = rl[2] + rl[1] + rl[0]
    i = process_list.popleft()
    rl[pcb[i]['priority']].remove(i)
    rl[pcb[i]['priority']].append(i)
    scheduler()

def scheduler():
    global rl
    process_list = rl[2] + rl[1] + rl[0]
    print(str(process_list[0])+" ", end="")

if __name__=='__main__':
    global rcb, pcb, rl
    filename = input()
    f = open(filename, 'r')
    text = f.readlines()
    for line in text:
        # print("RCB: %s\nPCB: %s\nRL: %s\n" % (rcb, pcb, rl))
        cmd = line.split()
        # print(cmd)
        if not cmd:
            continue
        elif cmd[0] == 'cr':
            create(int(cmd[1]))
        elif cmd[0] == 'de':
            destroy(int(cmd[1]))
        elif cmd[0] == 'rq':
            request(int(cmd[1]), int(cmd[2]))
        elif cmd[0] == 'rl':
            release(int(cmd[1]), int(cmd[2]))
        elif cmd[0] == 'to':
            timeout()
        elif cmd[0] == 'in':
            init()
    # init()
    # while True:
    #     print("RCB: %s\nPCB: %s\nRL: %s\n" % (rcb, pcb, rl))
    #     cmd = input("> ").split()
    #     # print(cmd)
    #     if cmd[0] == 'cr':
    #         create(int(cmd[1]))
    #     elif cmd[0] == 'de':
    #         destroy(int(cmd[1]))
    #     elif cmd[0] == 'rq':
    #         request(int(cmd[1]), int(cmd[2]))
    #     elif cmd[0] == 'rl':
    #         release(int(cmd[1]), int(cmd[2]))
    #     elif cmd[0] == 'to':
    #         timeout()
    #     elif cmd[0] == 'in':
    #         init()