# File Research: sources/os/plan9/9front/sys/src/cmd/clock.c

Graphical analog clock for Plan 9 draw/event. It opens a draw window, allocates simple color images, and redraws hour/minute hands plus twelve dots.

`circlept` computes positions by angle. `redraw` recalculates only when time or window rectangle changes, centers the clock, derives radius from window size, draws background/dots/hands, and flushes the image.

`eresized` reattaches on window resize and triggers redraw. `main` initializes draw/event, starts a 30-second timer, and provides a right-click menu with `exit`.

No filesystem logic; included as a small Plan 9 user command in the same source tree batch.
