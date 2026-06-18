# File Research: sources/os/bsd/freebsd-src/sys/sys/sdt.h

Statically Defined Tracing interface for FreeBSD kernel and userspace DTrace probe sites.

Key responsibilities:
- Defines userspace `DTRACE_PROBE` through `DTRACE_PROBE5` wrappers that call generated `__dtrace_*` symbols with unsigned-long arguments.
- In kernels without `KDTRACE_HOOKS`, compiles all SDT and DTrace macros to no-ops while preserving call-site syntax.
- In kernels with tracing, declares provider/probe/linker-set metadata and emits patchable tracepoints using machine-dependent asm.
- Provides `SDT_PROVIDER_DEFINE`, `SDT_PROBE_DEFINE*`, `SDT_PROBE*`, argument type metadata, translated argument metadata, and MIB probe wrappers.
- Defines SDT runtime structures: `sdt_tracepoint`, `sdt_argtype`, `sdt_probe`, and `sdt_provider`.

Important patterns:
- Probe definitions are registered through linker sets: `sdt_providers_set`, `sdt_probes_set`, and `sdt_argtypes_set`.
- `SDT_PROBE*` call sites use `asm goto` patchpoints so disabled probes are cheap and enabled probes can branch into `sdt_probe`/`sdt_probe6`.
- Argument types are string metadata used by DTrace consumers rather than C type enforcement.
- The public `DTRACE_PROBE*` macros are implemented on top of the SDT provider in kernel builds.

Research relevance:
- Central header for FreeBSD's low-overhead tracing ABI.
- Useful for understanding how kernel instrumentation is compiled in without forcing runtime cost when probes are disabled.
