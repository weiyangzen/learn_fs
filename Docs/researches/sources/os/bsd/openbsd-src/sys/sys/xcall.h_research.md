# File Research: sources/os/bsd/openbsd-src/sys/sys/xcall.h

Defines the CPU crosscall API. `struct xcall` wraps a function and argument; `struct xcall_cpu` holds four pending xcall slots and a soft interrupt handle for each CPU.

The header documents the MD integration requirements: CPU device dependency, `cpu_info` member, establish call, MD IPI hook, and dispatch at `IPL_SOFTCLOCK`. Kernel API sets an xcall, sends one to a CPU, synchronously runs a callback on a CPU, establishes per-CPU state, and dispatches pending calls.
