# File Research: sources/os/bsd/netbsd-src/sys/sys/kprintf.h

Defines kernel printf internals. It provides buffer sizing, output destination flags for console/tty/log/buffer/DDB, lock and initialization routines, the core `kprintf` formatter entry point, and log priority control.

Other kernel subsystems can reuse exact kernel formatting semantics. Important contracts are that `kprintf` and `klogpri` require the kprintf mutex where documented, and flags control locking/timestamp/output behavior. Risks are lock recursion and printing from panic/debug contexts.
