# File Research: sources/os/plan9/9front/sys/src/9/sgi/screen.h

Declares mouse/screen/devdraw interfaces shared by SGI screen, mouse, and draw code. It provides prototypes for cursor control, `flushmemscreen`, `attachscreen`, mouse tracking, mouse protocol helpers, and draw locking.

Defines `ishwimage(i)` as `0`, meaning hardware image acceleration is not advertised to `../port/devdraw.c`.
