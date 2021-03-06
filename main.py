from pynput import mouse
from pynput import keyboard
import time
import threading

key_count = 0
start_key = keyboard.Key.f10
stop_key = keyboard.Key.f11
keys = ('w', 's', 'a', 'd', 'q', 'e', 'c')

paused = False
started = False
chatOpen = False
finished = False

click_time_first = 0
click_time_last = 0
last_pressed = 0


def on_press(key):
    global started
    global key_count
    global paused
    global chatOpen
    global stop_key
    global last_pressed
    global click_time_last
    global click_time_first

    # check to see how much time passed since last press;
    # used to fix issue with holding a key down being recorded as multiple key presses
    click_time_last = time.time()
    elapsed = click_time_last - click_time_first
    click_time_first = time.time()

    if started:

        # 0.05 and less was observed time when holding down a key
        # holding down a key such as sprint key
        # it may vary on different machines
        if elapsed < 0.05 and key == last_pressed:
            return

        if key == stop_key or key == keyboard.Key.cmd_r:
            print("stopped listening")
            global finished
            finished = True
            return


        elif key == keyboard.Key.esc:
            if chatOpen:
                chatOpen = False
            else:
                paused = not paused

            last_pressed = keyboard.Key.esc
            return

        try:

            # if chat was opened and pressed enter - unpause
            if chatOpen and key == keyboard.Key.enter:
                chatOpen = False
                #print("closed chat")
                return

            # if neither paused and not writing in chat, listen normally
            if not paused and not chatOpen:
                # check if space
                if key == keyboard.Key.space:
                    key_count = key_count + 1
                    last_pressed = keyboard.Key.space
                # check if key equals to any of the movement keys defined at the top
                elif key.char in keys:
                    key_count = key_count + 1
                    last_pressed = key

                # check if chat was opened
                elif key.char == 't':
                    chatOpen = True

        except AttributeError:
            last_pressed = key
            return

        last_pressed = key
    else:

        if key == start_key:
            print("started listening")
            started = True
            return

# mouse listener, check if right or left click, when listening has started by using start key (f2 default), not paused and not chatting (esc,t)
def on_click(x, y, button, pressed):
    if started and not paused and not chatOpen:

        if (pressed and button == mouse.Button.left) or (pressed and button == mouse.Button.right):
            global key_count
            key_count += 1


def start_listening(k, m):
    k.start()
    m.start()


def stop_listening(k, m):
    k.stop()
    m.stop()


def convert_time(t):
    t = round(t)
    minute, sec = divmod(t, 60)
    hour, minute = divmod(minute, 60)
    return "%d:%02d:%02d" % (hour, minute, sec)


def main():
    global key_count

    key_listener = keyboard.Listener(on_press=on_press)
    mouse_listener = mouse.Listener(on_click=on_click)
    # running listeners on separate thread
    threading.Thread(start_listening(key_listener, mouse_listener)).start()

    print(f"press {start_key} to start, {stop_key} to end")

    results = []
    click_sum = 0
    t_start = 0
    t_end = 0
    t_temp = time.time()

    # append number of key presses to list every minute
    while not finished:
        if started:
            if paused or chatOpen:
                t_temp = time.time()
            if t_start == 0:
                t_start = time.time()
            t_end = time.time()

            # check if 1 second passed rather than 60; more results this way, giving more accurate data
            if (t_end - t_temp) > 4.8:
                t_temp = time.time()
                click_sum += key_count
                # as a result of halving check time, saving doubled apm
                results.append(key_count)
                key_count = 0

        # reducing loop frequency for efficiency, increase number of seconds if lagging
        # however the more delay the worse accuracy of results,
        # e.g. can result in checking second after normal time, giving a second worth of clicks more
        time.sleep(1)

    elapsed = t_end - t_start
    stop_listening(k=key_listener, m=mouse_listener)

    # only proceed if got anything to work with
    if len(results) > 2:

        # since getting measurements every 5 seconds, it will take 12 measurements to show rpm

        results_apm = []

        c = 0
        clicks = 0
        for i in results:
            if c < 13:
                clicks += i
                if c == 12:
                    results_apm.append(clicks)  # sum of 12 results will give APM
                    clicks = 0
                c += 1
            else:
                c = 0

        # need to account for last set of 12 clicks, as it may not be complete
        length_check = len(results_apm) % len(results)

        if length_check != (len(results)//12):
            results_apm = results_apm[:-1]


        # need an array for 'time' with the same size as 'results' array
        # using np.arange to populate list to correct size

        import matplotlib.pyplot as plt
        import numpy as np

        _ = round(elapsed)
        xpoints = np.arange(1, _, _ / len(results))
        ypoints = np.array(results)

        # plot graph
        plt.plot(xpoints, ypoints)
        plt.xlabel("Time (s)")
        plt.ylabel("Clicks in 5 seconds time")
        plt.title("Action key frequency during SA:MP gameplay")
        # plt.grid(True)
        plt.savefig('test_graph.png', bbox_inches='tight')
        # plt.show()

        # for larger amounts of data plot and save APM graph as well
        if len(results) > 5:
            xpoints = np.array(results)
            ypoints = np.arange(1, xpoints.size)

            plt.plot(xpoints, ypoints)
            plt.xlabel("Time (mins)")
            plt.ylabel("APM")
            plt.title("Actions per minute during SA:MP gameplay")
            plt.savefig('test_apm_graph.png', bbox_inches='tight')

        apm_avg = round(sum(results_apm) / len(results_apm), 1)
        apm_highest = max(results_apm)

        aps = round(apm_avg / 60, 1)
        aps_highest = round((max(results) / 5), 1)

        _ = ["run time = {convert_time(elapsed)}\n",
             f"key presses = {click_sum}\n",
             f"average apm = {apm_avg}\n",
             f"highest apm = {apm_highest}\n",
             f"average actions per second = {aps}\n",
             f"highest actions per second = {aps_highest}"]

        results_file = open("test_results.txt", "w")
        results_file.writelines(_)
        results_file.close()
        print("results saved")

    else:
        print("did not register enough key presses to display results\n"
              "let it run a while first!")


if __name__ == '__main__':
    main()






