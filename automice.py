import time
import json
from pynput import mouse

class MouseListener:
    def __init__(self):
        self.safe = True
        self.seq = []
        self.delay = 0
        self.start_time = 0
        self.t = 0
        self.stop_after = None
        self.stop_on = ''

    def _on_move(self, x, y):
        t = time.time()
        
        if self.stop_on == 'move' or (self.stop_after and t - self.start_time > self.stop_after):
            return False

        if self.safe and not self.stop_after and not self.stop_on and t - self.start_time > 10:
            return False
        
        event = {
            'type': 'move',
            'x': x,
            'y': y,
            'delay': t - self.t
        }
        
        self.t = t
        self.seq.append(event)

    def _on_click(self, x, y, button, pressed):
        t = time.time()
        
        if self.stop_on == 'click' or (self.stop_after and t - self.start_time > self.stop_after):
            return False
        
        if self.safe and not self.stop_after and not self.stop_on and t - self.start_time > 10:
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

    def _on_scroll(self, x, y, dx, dy):
        t = time.time()
        
        if self.stop_on == 'scroll' or (self.stop_after and t - self.start_time > self.stop_after):
            return False
        
        if self.safe and not self.stop_after and not self.stop_on and t - self.start_time > 10:
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
        
    def listen(self, delay:int=0, stop_after:int=None, stop_on:str='', safe:bool=True):
        """
        Listen for mouse events.
        
        :param delay: Number of seconds to wait before starting listener.
        :param stop_after: Return on next event after listening for this many seconds.
        :param stop_on: An event that stops the listener. One of move | click | scroll.
        :param safe: If False and no stop condition is given, the listener will run forever.
        :return: List of dicts describing each event.
        """
        
        self.safe = safe
        self.stop_after = stop_after
        self.stop_on = stop_on
        
        if delay:
            print(f'Waiting for {delay} seconds')
            time.sleep(delay)

        print('Starting listener')
        with mouse.Listener(on_move=self._on_move, on_click=self._on_click, on_scroll=self._on_scroll) as listener:
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

                
def run_mouse_events(fp:str, delay:int=0, safe:bool=True):
    """
    Execute a series of mouse events.
    
    :param fp: File path to read from.
    :param delay: Number of seconds to wait before running first event.
    :param safe: If True, function will return on next iteration after running for 10 seconds. Default is True.
    """
    
    controller = mouse.Controller()
    
    with open(fp, 'r', encoding='utf-8') as f:
        seq = json.load(f)
    
    if delay:
        print(f'Waiting for {delay} seconds')
        time.sleep(delay)
        
    start_time = time.time()
    
    print('Running events')
    for event in seq:
        if safe and time.time() - start_time > 10:
            return
        
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
