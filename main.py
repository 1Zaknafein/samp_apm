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

    # check to see how much time passed since last press; used to fix issue with holding a key down being recorded as multiple key presses
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
            # save results and end
            global finished
            finished = True
            return


        elif key == keyboard.Key.esc:
            if chatOpen:
                chatOpen = False
                #print("closed chat")
            else:
                paused = not paused
                #if paused:
                    #print("paused")
                #else:
                    #print("unpaused")
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
                    #print("opened chat")
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


def main():
    global key_count
    # in seconds

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

            # check if 30 seconds passed rather than 60; more results this way, giving more accurate data
            if (t_end - t_temp) > 30:
                t_temp = time.time()
                click_sum += key_count
                # as a result of halving check time, saving doubled apm
                results.append(key_count*2)
                key_count = 0

        #reducing loop frequency for efficiency, increase number of seconds if lagging
        # however the more delay the worse accuracy of results,
        # e.g. can result in checking 5 seconds after normal time, giving 5 seconds worth of clicks more
        time.sleep(2.5)

    elapsed = t_end - t_start
    stop_listening(k=key_listener, m=mouse_listener)

    # only proceed if got anything to work with
    if len(results) > 2:


        # need an array for 'time' with the same size as 'results' array
        # using np.arange to populate list to correct size


        y = []
        for i in range(round(elapsed)):
            y.append(i)



        import matplotlib.pyplot as plt
        import numpy as np

        _ = round(elapsed)
        xpoints = np.arange(1, _, _ / len(results))


        print(len(results))
        print(xpoints.size)
        # print("total key presses in ~", round(elapsed, 2), "s time:", click_sum)

        # numpy array for pyplot
        #xpoints = np.array(y)
        ypoints = np.array(results)

        # plot graph
        plt.plot(xpoints, ypoints)
        plt.xlabel("time")
        plt.ylabel("APM")
        # plt.grid(True)
        plt.savefig('test_graph.png', bbox_inches='tight')
        # plt.show()

        apm_avg = round(sum(results) / len(results), 1)
        aps = round(apm_avg / 60, 1)

        _ = ["Test results:\n",
             f"run time = {convert_time(elapsed)}\n",
             f"key presses = {click_sum}\n",
             f"average apm = {apm_avg}\n",
             f"average actions per second = {aps}"]

        results_file = open("test_results.txt", "w")
        results_file.writelines(_)

        results_file.close()

        print("results saved")

    else:
        print("did not register enough key presses to display results\n"
              "let it run for abit first!")


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


if __name__ == '__main__':
    main()
