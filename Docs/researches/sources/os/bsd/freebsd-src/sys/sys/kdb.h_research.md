# File Research: sources/os/bsd/freebsd-src/sys/sys/kdb.h

Kernel debugger frontend/backend interface. It defines backend callback types for init, trace, per-thread trace, and trap handling, plus `struct kdb_dbbe` and `KDB_BACKEND()` linker-set registration.

Globals expose debugger active state, panic/trap entry flags, selected backend, current trap frame, PCB context, and current thread. APIs cover alternate breaks, entering/reentering debugger, backtraces, backend selection, initialization, panic/reboot, thread lookup/iteration/selection, and trap dispatch.

`kdb_why` reason strings classify debugger entry causes, including panic, kassert, trap, sysctl, boot flags, witness, VFS lock, watchdog, DTrace, and reboot. It also defines alternate-break return requests and debug access type constants.
