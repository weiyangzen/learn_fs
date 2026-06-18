# sources/user-network-fs/nfs-ganesha/src/tracing/lttng_defines.c

Purpose: `lttng_defines.c` emits weak LTTng tracepoint symbols for code that calls tracepoints while allowing tracing to remain disabled unless the real probe module is loaded.

Important macros and includes: under `USE_LTTNG`, it defines `TRACEPOINT_DEFINE` and `TRACEPOINT_PROBE_DYNAMIC_LINKAGE`, then includes `gsh_lttng/generated_traces/generated_lttng.h` unless `LTTNG_PARSING` is set. These macros drive LTTng tracepoint header expansion.

Control flow: there is no runtime control flow. Compilation of this file into targets via `ganesha_trace_symbols` supplies weak functions; dynamic loading of `libganesha_trace.so` supplies overriding implementations from `lttng_probes.c`.

State and persistence: no persistent or mutable state. Symbol tables and link behavior are the meaningful artifact.

Dependencies and integration points: depends on generated trace headers and LTTng macro semantics. It is linked into any target that directly references tracepoints.

Risks: including generated trace headers more than once with definition macros in one binary can cause duplicate symbols. If consumers forget `ganesha_trace_symbols`, tracepoint calls may fail to link. If `USE_LTTNG` is off, this compiles to an inert file.

Test signals: build LTTng-enabled targets with and without loading the trace module; verify link success and that weak definitions do not emit events until overridden.
