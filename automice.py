import time
import json
from pynput import mouse

class MouseListener:
    def __init__(self, safe:bool=True):
        self.safe = safe
        self.seq = []
        self.delay = 0
        self.start_time = 0
        self.t = 0
        self.stop_after = None
        self.stop_on = ''

    def on_move(self, x, y):
        t = time.time()
        
        if self.stop_on == 'move' or (self.stop_after and t - self.start_time > self.stop_after):
            return False
        
        event = {
            'type': 'move',
            'x': x,
            'y': y,
            'delay': t - self.t
        }
        
        self.t = t
        self.seq.append(event)

    def on_click(self, x, y, button, pressed):
        t = time.time()
        
        if self.stop_on == 'click' or (self.stop_after and t - self.start_time > self.stop_after):
            return False
        
        b = ''
        
        if button == mouse.Button.left:
            b = 'left'
        elif button == mouse.Button.right:
            b = 'right'
        else:
            return True
        
        event = {
            'type': 'click',
            'x': x,
            'y': y,
            'button': b,
            'pressed': pressed,
            'delay': t - self.t
        }
        
        self.t = t
        self.seq.append(event)

    def on_scroll(self, x, y, dx, dy):
        t = time.time()
        
        if self.stop_on == 'scroll' or (self.stop_after and t - self.start_time > self.stop_after):
            return False
        
        event = {
            'type': 'scroll',
            'x': x,
            'y': y,
            'dx': dx,
            'dy': dy,
            'delay': t - self.t
        }
        
        self.t = t
        self.seq.append(event)
        
    def listen(self, delay:int=0, stop_after:int=None, stop_on:str=''):
        """
        Listen for mouse events.
        
        :param delay: Number of seconds to wait before starting listener.
        :param stop_after: After listening for this many seconds, any subsequent event will stop the listener.
        :param stop_on: An event that stops the listener. One of move | click | scroll.
        :return: List of dicts describing each event.
        """
        
        if stop_after:
            self.stop_after = stop_after

        if stop_on:
            self.stop_on = stop_on
        
        if delay:
            time.sleep(delay)

        with mouse.Listener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll) as listener:
            self.start_time = time.time()
            self.t = time.time()
            listener.join()

        return self.seq

    def save(self, fp:str):
        """
        Save events to JSON file.
        
        :param fp: File path where events will be saved.
        """
        with open(fp, 'w', encoding='utf-8') as f:
            json.dump(self.seq, f)

                
def run_mouse_events(fp:str, delay:int=0):
    """
    Execute a series of mouse events.
    
    :param fp: File path to read from.
    :param delay: Number of seconds to wait before starting execution.
    """
    
    controller = mouse.Controller()
    
    with open(fp, 'r', encoding='utf-8') as f:
        seq = json.load(f)
    
    time.sleep(delay)
    
    for event in seq:
        time.sleep(event['delay'])
        controller.position = (event['x'], event['y'])
        
        match event['type']:
            case 'click':
                match event['button']:
                    case 'left':
                        match event['pressed']:
                            case True:
                                controller.press(mouse.Button.left)
                            case False:
                                controller.release(mouse.Button.left)
                    case 'right':
                        match event['pressed']:
                            case True:
                                controller.press(mouse.Button.right)
                            case False:
                                controller.release(mouse.Button.right)
                        
            case 'scroll':
                controller.scroll(event['dx'], event['dy'])
        