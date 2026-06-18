# File Research: sources/os/plan9/plan9/sys/src/9/port/sysproc.c

Implements process, exec, memory, synchronization, wait, note, and time syscalls.

Process creation:
- `sysrfork` validates rfork flags, supports in-place group changes when `RFPROC` is absent, and creates child processes when present.
- Duplicates or shares memory, fd, namespace, rendezvous, and environment groups based on flags.
- Builds child return frame through `forkchild`, copies identity/debug/note state, inherits priority/wiring, and readies the child.

Exec:
- `sysexec` opens an executable, supports a.out and `#!` script indirection, validates text/entry/layout, counts/copies argv, creates a temporary stack, commits new text/data/BSS/stack segments, closes `CCEXEC` fds, attaches shared text image, resets notify/debug state, flushes MMU, and returns through `execregs`.
- `shargs` parses interpreter lines.

Exit/wait/error/notify:
- `sysexits` validates/caps exit status and calls `pexit`.
- `sys_wait` returns old wait format.
- `sysawait` returns modern formatted wait text.
- `werrstr`, `generrstr`, `syserrstr`, and old `sys_errstr` swap user/kernel error strings.
- `sysnotify` installs a notify handler; `sysnoted` validates note return protocol.

Memory syscalls:
- `syssegbrk`, `syssegattach`, `syssegdetach`, `syssegfree`, and compatibility `sysbrk_`.
- Detach rejects the initial stack segment and flushes MMU after removing mappings.

Rendezvous and semaphores:
- `sysrendezvous` matches waiters by tag in the current `Rgrp`, otherwise sleeps in `Rendezvous` state.
- Semaphore implementation uses `Sema` nodes in the owning `Segment`, compare-and-swap on user memory, explicit wait-list locking, and careful wakeup passing.
- `syssemacquire`, `systsemacquire`, and `syssemrelease` expose blocking, timed, and release operations.

Time and misc:
- `syssleep` yields for nonpositive sleep, otherwise sleeps at least one tick.
- `sysalarm` delegates to `procalarm`.
- `sysnsec` writes `todget(nil)` to user memory.
- `sysr1` invokes `checkpagerefs` for diagnostics.
- `l2be` converts old executable header fields.

Cautions:
- The semaphore block has extensive race documentation; it depends on `cmpswap`, `coherence`, and strict wakeup handoff.
- `sysexec` commits in phases with nested error handlers; after commit, old memory/fds may already be released.
