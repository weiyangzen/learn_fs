# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/trace.h

Purpose: Xen public tracing ABI header. It defines trace class/event IDs and the trace-buffer record layout used by Xen trace consumers.

Key interfaces:
- Trace class masks for general, scheduler, dom0 ops, HVM, memory, PV, shadow, hardware, guest.
- Scheduler subclass encoding and per-scheduler event helper macro.
- Event IDs for scheduler, memory, PV hypercalls/traps, shadow, HVM exits/handlers, power management, and IRQ handling.
- Record structs: `t_rec`, `t_buf`, `t_info`.

Integration notes: Used by control tools that map Xen trace buffers obtained via sysctl tbuf operations.

Risk/attention points: The trace record bitfields and flexible-array metadata are ABI structures. Consumers must understand optional cycle-count inclusion and `extra_u32` lengths.
