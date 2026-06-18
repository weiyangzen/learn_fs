# File Research: sources/os/bsd/netbsd-src/sys/sys/sdt.h

Read completely: 512 lines.

This header implements statically defined tracing macros for userland and kernel code. Userland gets `DTRACE_PROBE*` macros that call external `__dtrace_provider___name` symbols with unsigned-long arguments.

In the kernel, behavior splits on `KDTRACE_HOOKS`. Without hooks, provider/probe declarations and probe macros compile away while consuming arguments to avoid warnings. With hooks, macros create `sdt_provider`, `sdt_probe`, and `sdt_argtype` objects in linker sets and dispatch enabled probes through `sdt_probe_func`.

It defines argument-type registration, 0 through 7 argument SDT probe macros, translated argument variants, `DTRACE_PROBE*` compatibility macros, provider/probe structures, init/exit functions, a stub function, and `SET_ERROR` instrumentation when DTrace hooks are enabled.

Risks: this header emits static objects and link-set entries via macros. Provider/module/function/name tokens become symbol names, and the 6/7-argument probes use function-pointer casts beyond the base five-argument function typedef.
