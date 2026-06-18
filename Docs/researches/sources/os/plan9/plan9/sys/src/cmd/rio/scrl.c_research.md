# File Research: sources/os/plan9/plan9/sys/src/cmd/rio/scrl.c

Read status: complete, 183 lines.

This file implements window scrollbar drawing and scrollbar interaction. `scrpos` maps visible text range to scrollbar thumb rectangle, with scaling for very large buffers. `wscrdraw` redraws the scroll gutter using a temporary image.

`wscroll` handles button-specific scrolling: button 2 maps thumb position proportionally to buffer origin; button 1 and button 3 scroll by line/page-like positions. `wscrsleep` uses the timer subsystem and mouse movement to pace repeated scrolling.

Filesystem relevance: no filesystem logic, but it controls visual navigation over the text exposed through window files.
