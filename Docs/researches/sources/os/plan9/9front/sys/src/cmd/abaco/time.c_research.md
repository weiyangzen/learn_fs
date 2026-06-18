# File Research: sources/os/plan9/9front/sys/src/cmd/abaco/time.c

Small timer scheduler for Abaco event loops.

Key responsibilities:
- Maintains reusable `Timer` objects and a global timer-start channel.
- Starts a timer proc that tracks active timers in milliseconds.
- Supports starting, canceling, and stopping/recycling timers.
- Delivers timer expiration with nonblocking sends to each timer’s channel.

Important behavior:
- The timer proc sleeps at minimum increments and subtracts elapsed time from all active timers.
- Canceled timers and successfully delivered timers are removed and recycled.
- When no timers are active, the proc blocks waiting for a new timer.

Dependencies:
- Uses Plan 9 thread channels and `nsec()`.

Notable risks:
- Timer free list is not locked; code assumes timer operations occur in the process/thread model without conflicting concurrent mutation.
