# File Research: sources/os/bsd/freebsd-src/sys/sys/timers.h

Kernel POSIX timer management header.

Key responsibilities:
- Defines kernel `struct itimer` with mutex, sigevent, current timer specification, owning process, flags, use count, overrun counters, clock id, signal info, and callout.
- Defines timer lifecycle flags for deleting, wanted, and process-stopped states.
- Sets per-process `TIMER_MAX` to 32 and defines lock/unlock helpers.
- Defines `struct itimers` as the per-process timer table.
- Defines `struct kclock`, an implementation vtable for create, settime, delete, and gettime operations.
- Declares exec/exit cleanup and signal-acceptance helpers.

Dependencies:
- Includes `sys/time.h`; kernel users need mutex, sigevent, proc, ksiginfo, and callout definitions from surrounding includes.

Notable risks:
- Timer lifecycle combines callouts, signal delivery, process exit/exec, and locking; reference/use-count transitions must be carefully synchronized.
- `TIMER_MAX` is part of process resource behavior and compatibility expectations.
