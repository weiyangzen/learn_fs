# File Research: sources/os/plan9/9front/sys/src/cmd/histogram.c

Implements a live graphical histogram window fed by numbers from stdin.

Key points:
- Creates a new Plan 9 window and initializes draw, mouse, and keyboard controls.
- Reads numeric values from stdin in a separate process using `Biobuf`.
- Maintains a rolling `double` array sized to the current graph width.
- `updatehistogram()` shifts previous samples and draws the newest column at the right edge.
- `redrawhistogram()` handles full window redraw and resize, including title, border, current numeric value, and all stored samples.
- Uses selectable color palettes through `-c`.
- Options:
  - `-v maxv` set displayed maximum
  - `-s scale` set input scaling
  - `-t title` set title
  - `-r rect` set window rectangle
  - `-h` keep running after input EOF
  - `-c index` select palette
- Event loop handles incoming data, mouse menu exit, Delete key exit, and resize events.

Dependencies and interactions:
- Uses Plan 9 draw, mouse, keyboard, thread, and bio libraries.
- No persistent filesystem logic beyond stdin and window creation.

Research relevance:
- A compact Plan 9 UI utility demonstrating channel-based event multiplexing, live redraw, and streaming visualization.
