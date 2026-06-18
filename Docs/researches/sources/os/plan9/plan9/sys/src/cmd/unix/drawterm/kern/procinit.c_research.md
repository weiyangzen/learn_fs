# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/procinit.c

This file initializes the hosted drawterm process table and creates kernel processes.

Key behavior:
- `procinit0` allocates initial `Proc` state for the main host thread, including `pgrp`, `rgrp`, `fgrp`, `egrp`, error buffers, and default name.
- `newproc` allocates and initializes a new `Proc`.
- `kproc` names a process, assigns its function/argument, wires shared groups from `up`, and starts it through `osnewproc`.

Important details:
- New kernel processes share the current process's namespace, rendezvous group, file group, and environment group by pointer/refcount convention.
- Host-specific thread creation is delegated to `posix.c` or `win32.c`.
