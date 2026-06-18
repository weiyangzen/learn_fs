# File Research: sources/os/plan9/plan9/sys/src/cmd/clock.c

Graphical analog clock using Plan 9 draw/event libraries. Allocates simple color images for background, hands, and hour dots. `redraw` computes center/radius, hour/minute angles from local time, redraws only when time or window rectangle changes, and flushes display.

Main loop listens for mouse events and timer ticks; right-button menu contains only `exit`. `eresized` reattaches the window and redraws.
