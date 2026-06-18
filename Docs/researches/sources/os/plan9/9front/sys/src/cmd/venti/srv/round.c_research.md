# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/round.c

`round.c` implements a small round/kick synchronization primitive used by background cache/write processes. A `Round` has start, finish, and delayed-wait rendezvous points plus generation counters (`last`, `current`, `next`).

`kickround()` requests another round and can wait until the current requested generation completes. `waitforkick()` is called by the worker side to publish completion and sleep for the next request. `delaykickroundproc()` coalesces delayed kicks by sleeping for `delaytime` and only kicking if no newer round has started.

The code is a lightweight event coalescing mechanism for periodic flushing/prefetch work.
