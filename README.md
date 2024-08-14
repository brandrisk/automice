# Automice

Simulates mouse movements.

## install

- Clone repo
- `pip install .`

## example
Record a series of mouse events and save to example.json.

```py
from automice import MouseListener, run_mouse_events

listener = MouseListener()
listener.listen(stop_on='scroll')
listener.save('example.json')
```

Load mouse events from example.json and run them.

```py
run_mouse_events('example.json')
```
