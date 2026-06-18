# sources/test-tools/stress-ng/core-affinity.h

Purpose: public affinity API declarations.

Important APIs and control flow: exposes CPU affinity setting, optional parser for `cpu_set_t`, CPU migration, usable CPU list allocation, and free helpers.

State and persistence: no state in the header; callers must free arrays returned by `stress_affinity_cpus_get`.

Dependencies and integration: includes `config.h` and relies on `stress_args_t`, `cpu_set_t`, `uint32_t`, and `bool` from the wider stress-ng include graph.

Risks and test signals: prototypes are conditionally visible for `HAVE_CPU_SET_T`; mismatched feature macros between translation units would break builds. Signal is successful compilation on affinity and non-affinity platforms.
