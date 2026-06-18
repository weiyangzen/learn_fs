# sources/test-tools/stress-ng/core-rapl.h

Purpose: declares the RAPL measurement contract for Linux/x86 builds. It isolates RAPL-specific structs and functions behind the `STRESS_RAPL` feature gate.

Important APIs/types/functions: `STRESS_RAPL_DOMAINS_MAX` caps exported per-stressor arrays at 32. `stress_rapl_data_t` stores previous energy, previous sample time, and computed watts. `stress_rapl_domain_t` represents one sysfs powercap domain in a linked list. `stress_rapl_t` is the compact per-stressor stats payload with a read time and domain watts array. Public functions cover domain discovery/free, raplstat sampling, stressor sampling, and YAML/info dumping.

Control flow: no runtime logic in the header; inclusion depends on `__linux__` and `STRESS_ARCH_X86`.

State and persistence: describes mutable in-memory sampling state only. Callers own `stress_rapl_domain_t` list lifetime and embed/copy `stress_rapl_t` in stressor stats.

Dependencies/integration: includes `core-arch.h` and `stress-ng.h`, and uses `FILE` plus `stress_list_item_t` in declarations. It integrates with metrics collection and per-stressor statistics.

Risks: consumers must guard references with `STRESS_RAPL`; otherwise non-x86 or non-Linux builds will not see these types. The fixed domain array means the list can represent more domains than the compact stats object can export.

Test signals: compile both with and without Linux/x86 RAPL support; verify callers keep feature guards around struct fields and functions.
