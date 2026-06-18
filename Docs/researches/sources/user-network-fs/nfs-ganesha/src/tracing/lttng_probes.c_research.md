# sources/user-network-fs/nfs-ganesha/src/tracing/lttng_probes.c

Purpose: `lttng_probes.c` instantiates the actual LTTng tracepoint probes for Ganesha's loadable tracing module.

Important macros and includes: under `USE_LTTNG`, it defines `TRACEPOINT_CREATE_PROBES` and includes `gsh_lttng/generated_traces/generated_lttng.h` unless `LTTNG_PARSING` is defined. This is the canonical LTTng pattern for creating tracepoint probe implementations.

Control flow: no explicit runtime control flow. The generated probe symbols are loaded with the `ganesha_trace` module and override/couple with the weak symbols from `lttng_defines.c`.

State and persistence: no local state. Runtime tracing state is handled by LTTng and the dynamic loader.

Dependencies and integration points: depends on generated trace headers, `USE_LTTNG`, and the CMake module target. It must include every trace header once, according to the file comments, to avoid missing or duplicate probes.

Risks: including generated headers from multiple probe compilation units can duplicate probes; missing generated headers disables trace coverage. Runtime behavior depends on loading the module in the right process address space.

Test signals: build `ganesha_trace`, load it in an LTTng-enabled deployment, and verify events flow for tracepoints that otherwise link through weak definitions.
