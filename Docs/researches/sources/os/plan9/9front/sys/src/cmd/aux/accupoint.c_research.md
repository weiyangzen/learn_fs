# File Research: sources/os/plan9/9front/sys/src/cmd/aux/accupoint.c

Mouse-event filter for AccuPoint devices. It converts buttons 4 and 5 into simulated button 2 behavior.

Important behavior:
- Reads Plan 9 mouse event records from stdin: one byte plus four 12-character numeric fields.
- Writes transformed mouse records to stdout.
- Button 5 generates a quick button-2 click and suppresses bounce.
- Button 4 simulates holding button 2; because the hardware lacks up events, timeout via `alarm(550)` clears the simulated hold.
- Native button 2 cancels simulated mode.

Filesystem/IO relevance:
- Acts as a stream filter in front of mouse event consumers, transforming device file event records.
