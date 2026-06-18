# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/round.c

Purpose: Provides a reusable “round” synchronization primitive for background server tasks.

Key behavior:
- `waitforkick` blocks a worker until another round is requested, then advances current/next counters.
- `kickround` requests a round and optionally waits until it completes.
- `delaykickround` and `delaykickroundproc` coalesce delayed kicks: if no newer kick arrives before the delay, a synchronous kick is issued.

Dependencies:
- Uses Plan 9 `QLock`, `Rendez`, sleep, and tracing.

Notable details:
- Used for tasks where repeated requests can be collapsed into one later pass, such as cache writeback.
