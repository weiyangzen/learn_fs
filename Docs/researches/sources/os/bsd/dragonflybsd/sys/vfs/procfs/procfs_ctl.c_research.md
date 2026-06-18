# File Research: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_ctl.c

This file implements writes to `/proc/<pid>/ctl`. It maps command strings such as `attach`, `detach`, `step`, `run`, and `wait`, plus signal names, to process debugging/control actions.

`procfs_control()` enforces execution-state and authorization checks, blocks tracing PID 1 at securelevel > 0, attaches by setting `P_TRACED`, reparenting to the tracer, and stopping the target, detaches by clearing tracing state and reparenting back when possible, single-steps through `procfs_sstep()`, resumes stopped processes, and waits for trace stop states.

`procfs_doctl()` accepts only writes, reads a bounded user string via `vfs_getuserstr()`, resolves it against control commands or signal names, and either calls `procfs_control()` or sends/queues a signal.

Research notes: the target process token must be held on entry. The file is debugger-sensitive and relies on `CHECKIO`, `p_trespass()`, securelevel checks, and stopped/traced process state.
