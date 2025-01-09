import re
import random

# This function extracts IPC values for each thread from the perf_thread_X.txt file which is the output of the perf command
def parse_perf_log(thread_id):
    
    filename = f"perf_thread_{thread_id}.txt"
    
    try:
        with open(filename, 'r') as f:
            for line in f:
                # Look for the line containing "insn per cycle"
                if "insn per cycle" in line:
                    # Extract the IPC value using regex
                    match = re.search(r"#\s+([0-9.]+)\s+insn per cycle", line)
                    if match:
                        ipc_value = float(match.group(1))
                        return ipc_value
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return None

    print(f"No IPC information found in {filename}.")
    return None

def main():
    # Collect IPC values for each thread
    ipc_values = {thread_id: parse_perf_log(thread_id) for thread_id in range(3)}
   
    # Sort threads by IPC values in ascending order
    sorted_threads = sorted(ipc_values, key=ipc_values.get)
    min1_thread = sorted_threads[0]
    min2_thread = sorted_threads[1]
    max_thread = sorted_threads[2]

    # By default unpinning threads i.e. setting affinity to -1 
    affinity = {}

    # Assign the thread with minimum IPC to a random core (logical core 0/1/2/3)
    affinity[min1_thread] = random.choice([0,1,2,3])

    # Check if minimum two IPC values are same then allocate different physical cores to these two threads and unpin the third thread with maximum IPC value  
    if ipc_values[min1_thread] == ipc_values[min2_thread]:
        # If equal, assigning separate physical cores to min1_thread (least IPC) and min2_thread (second-lowest IPC)
        if affinity[min1_thread] in [0,1]:
            affinity[min2_thread] = random.choice([2,3])
        else:
            affinity[min2_thread] = random.choice([0,1])
        #Unpinning the thread with maximum IPC value
        affinity[max_thread] = -1
    else:
        # Otherwise, assigning thread with minimum IPC value to a separate physical core and remaining two threads share the other physical core 
        if affinity[min1_thread] in [0,1]:
            affinity[min2_thread] = random.choice([2,3])
            if affinity[min2_thread] == 2:
                affinity[max_thread] = 3
            else:
                affinity[max_thread] = 2
        else:
            affinity[min2_thread] = random.choice([0,1])
            if affinity[min2_thread] == 0:
                affinity[max_thread] = 1
            else:
                affinity[max_thread] = 0

    # Write the affinity settings to a file affinity.txt
    with open("affinity.txt", "w") as f:
        for thread_id, core in affinity.items():
            f.write(f"Thread {thread_id}: {core}\n")


if __name__ == "__main__":
    main()
