# sources/test-tools/stress-ng/core-rapl.c

Purpose: discovers Intel RAPL powercap domains on Linux/x86, samples energy counters, converts deltas to watts, and emits per-stressor RAPL summaries.

Important APIs/types/functions: `stress_rapl_domains_get` scans `/sys/class/powercap` for `intel-rapl*` entries with readable `energy_uj`, records sysfs names, display domain names, max energy range, and sorted list indexes. `stress_rapl_domains_free` releases the linked list. `stress_rapl_power_raplstat_get` and `stress_rapl_power_stressor_get` share `stress_rapl_power_get`; the latter copies per-domain values into `stress_rapl_t`. `stress_rapl_dump` prints harmonic-mean watts for each stressor instance set.

Control flow: discovery opens the powercap directory, filters non-RAPL entries, validates energy readability, normalizes package names, rejects duplicate display domains, then inserts domains in sorted order. Sampling reads `energy_uj`, handles zero readings by reusing the previous value, detects wraparound using `max_energy_range_uj`, and only updates power if at least 0.25 seconds elapsed and the computed watts are positive. Dumping iterates stressor list items, skips ignored runs, aggregates instance power readings by domain, and writes both info and YAML output.

State and persistence: per-domain previous energy/time/power is held in the linked list for two consumers: raplstat and per-stressor sampling. Sysfs is read-only; no persistent system configuration is changed.

Dependencies/integration: compiled only under `STRESS_RAPL` from Linux/x86 guards. Uses `stress_time_now`, `stress_capabilities_check`, logging/YAML helpers, and `stress_list_item_t` stats fields.

Risks: sysfs permissions often require root or powercap access. Domain indexing is capped by `STRESS_RAPL_DOMAINS_MAX`; extra domains are silently skipped in per-stressor copies/dumps. Harmonic mean suppresses zero/unavailable samples, so missing samples can bias output.

Test signals: systems with no RAPL, unreadable `energy_uj`, wraparound-capable counters, multi-domain packages, and YAML metrics runs. Mocked sysfs tests should verify duplicate-domain filtering and 0.25 second gating.
