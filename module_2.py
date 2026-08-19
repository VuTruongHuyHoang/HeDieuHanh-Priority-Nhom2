def priority_non_preemptive(processes):
    sorted_processes = sorted(processes, key=lambda p: p['arrival_time'])
    
    ready_queue = []
    execution_order = []
    current_time = 0
    process_index = 0
    
    while len(execution_order) < len(sorted_processes):
        while (process_index < len(sorted_processes) and 
               sorted_processes[process_index]['arrival_time'] <= current_time):
            ready_queue.append(sorted_processes[process_index])
            process_index += 1
        
        if not ready_queue:
            if process_index < len(sorted_processes):
                current_time = sorted_processes[process_index]['arrival_time']
            continue
        
        selected = min(ready_queue, key=lambda p: (p['priority'], p['arrival_time']))
        ready_queue.remove(selected)
        
        start_time = max(current_time, selected['arrival_time'])
        completion_time = start_time + selected['burst_time']
        current_time = completion_time
        
        execution_order.append(selected['pid'])
    
    return execution_order