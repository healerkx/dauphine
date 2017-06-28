

from threading import Timer

import time
import re

class Clock:

    time_format_engine_list = list()

    follower_map = dict()

    last_emit_second = 0

    def __init__(self):
        pass

    @staticmethod
    def register(engine, trigger):
        """
        """
        if trigger.startswith('every-'):
            time_format = "\d\d\d\d-"
            if trigger.startswith('every-month'):
                time_format += ("\d\d-" + trigger[12:].strip())
            elif trigger.startswith('every-day'):
                time_format += ("\d\d-\d\d" + trigger[10:].strip())
            elif trigger.startswith('every-hour'):
                time_format += ("\d\d-\d\d \d\d:" + trigger[11:].strip())
            elif trigger.startswith('every-minute'):
                time_format += ("\d\d-\d\d \d\d:\d\d:" + trigger[13:].strip())
            elif trigger.startswith('every-second'):
                time_format += "\d\d-\d\d \d\d:\d\d:\d\d"

            Clock.time_format_engine_list.append((re.compile(time_format), engine))
        elif trigger.startswith('after'):
            action_before_info = trigger[6:]
            action_before = action_before_info.strip()
            delay = 0
            if '@delay' in action_before_info:
                delay_pos = action_before_info.index('@delay')
                action_before = action_before_info[:delay_pos].strip()
                delay = int(action_before_info[delay_pos + 6:].strip())

            
            # TODO: Delay
            if action_before in Clock.follower_map:
                Clock.follower_map[action_before].append((engine, delay))
            else:
                Clock.follower_map[action_before] = [(engine, delay)]
            

    @staticmethod
    def on_every_second():
        current_second = int(time.time())
        if Clock.last_emit_second == current_second:
            return
        
        Clock.last_emit_second = current_second
        
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_second))
        
        for (time_format, engine) in Clock.time_format_engine_list:
            if time_format.match(current_time):
                print('Trigger on', current_time)
                engine.run()

    @staticmethod
    def trigger_followers(run_func, engine, context):
        """
        TODO: run_func? 
        """
        if engine.name not in Clock.follower_map:
            return
        followers = Clock.follower_map[engine.name]
        for (follower, delay) in followers:
            # TODO: Delay
            if delay == 0:
                follower.run(context)
            else:
                Timer(delay, run_func, (follower, context)).start()
        

    @staticmethod
    def tick():
        Clock.on_every_second()
        # If set interval=1s, some second frames would be lost.
        timer = Timer(.5, Clock.tick)
        timer.start()