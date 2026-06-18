# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/periodic.c

Minimal periodic callback thread abstraction.

`periodicAlloc` stores a callback, argument, and interval, clamps very small intervals to at least 10 ms, and starts a worker thread. The worker sleeps in bounded increments, invokes the callback when due, catches up the next scheduled time, and exits/free itself when `periodicKill` sets the die flag.

It is used for cache sync, filesystem metadata flush, and snapshot scheduling.
