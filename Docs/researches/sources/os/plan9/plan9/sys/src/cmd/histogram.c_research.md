# File Research: sources/os/plan9/plan9/sys/src/cmd/histogram.c

Graphical live histogram/strip-chart utility reading numeric values from stdin.

- Supports `histogram [-h] [-c index] [-r minx,miny,maxx,maxy] [-s scale] [-t title] [-v maxv]`.
- Creates a new window, initializes drawing, mouse, keyboard, and a reader process.
- Reader parses one numeric token per input line and sends doubles over a channel.
- Maintains a rolling `double` array sized to the drawable width; new values shift old samples right.
- Draws colored vertical one-pixel bands with a dot-height transition between previous and current values.
- Handles resize redraws, button-3 exit menu, and Delete-key exit.

Dependencies are Plan 9 draw/thread/mouse/keyboard/Bio APIs.

Notable concerns: display buffer grows with window width; the program exits when stdin closes unless `-h` is set. Palette index is modulo the number of color schemes.
