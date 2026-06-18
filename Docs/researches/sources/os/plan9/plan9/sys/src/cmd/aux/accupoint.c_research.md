# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/accupoint.c

Mouse-event filter for AccuPoint devices. It converts buttons 4 and 5 into simulated button 2 behavior for Plan 9 mouse streams.

Button 4 is treated as press-and-hold button 2 with timeout-based release; button 5 generates a quick button-2 click and suppresses bounce. The program reads and writes standard Plan 9 mouse event records on stdin/stdout and uses alarm notifications for release timing.
