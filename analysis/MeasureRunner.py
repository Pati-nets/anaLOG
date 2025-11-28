import sys
import time
import threading
import math
import Constants

def get_pressed_key():
    """
    Returns a single pending keypress from the input buffer if available, otherwise None.
    - The function does NOT wait for a key press.
    - If multiple keys were pressed previously, only the first unprocessed one is returned.
    - Returns None if no key is waiting in the buffer.
    """
    if sys.platform.startswith("win"):
        import msvcrt
        return msvcrt.getwch() if msvcrt.kbhit() else None
    else:  # Unix-based (Linux, macOS)
        import select, termios, tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            if select.select([sys.stdin], [], [], 0)[0]:
                pressed_key = sys.stdin.read(1)
                return pressed_key
            return None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def clear_input_buffer():
    """
    Removes all pending keypresses from the input buffer so that only future keypresses are considered.
    """
    if sys.platform.startswith("win"):
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getwch()
    else: # Unix-based (Linux, macOS)
        # buffer clearing not necessary on unix systems
        pass

def timed_measure_calculation(measure, log_or_model, im=None, fm=None):
    """
    Executes the calculation of a complexity measure in a separate thread.
    - Waits silently for a predefined number of seconds.
    - If the measure takes longer, a warning is displayed.
    - Then the user can press Ctrl+A to abort the current measure.
    - Aborted measures return -inf.
    """
    result = {"done": False, "value": None}

    # Worker Thread: actually runs the complexity measure calculation
    def worker():
        try:
            if im is not None and fm is not None:
                result["value"] = measure.calculate_for(log_or_model, im, fm)
            else:
                result["value"] = measure.calculate_for(log_or_model)
        finally:
            result["done"] = True

    start = time.time()
    t = threading.Thread(target=worker, daemon=True)
    t.start()

    # Wait silently for up to `timeout_seconds` seconds
    t.join(timeout=Constants.timeout_seconds)
    if result["done"]:
        # Measure finished within the timeout → return immediately
        return result["value"]

    # Measure still running: notify user and allow abort
    print(f"\nCalculating measure '{measure}' may take a while.")
    print(f"Press {Constants.abort_key["label"]} to abort this measure, or wait to continue...")

    aborted = False
    clear_input_buffer()
    while not result["done"]:
        if get_pressed_key() == Constants.abort_key["code"]:
            aborted = True
            break
        time.sleep(0.001)

    # If aborted: stop waiting and return -inf
    if aborted:
        elapsed = int(time.time() - start)
        print(f"Measure '{measure}' aborted after {elapsed}s. Marking as -inf. Proceeding to next measure.")
        return -math.inf

    # If finished normally after the warning → return value
    elapsed = int(time.time() - start)
    print(f"Measure '{measure}' finished in {elapsed}s. Proceeding to next measure.")
    return result["value"]
