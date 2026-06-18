# sources/test-tools/stress-ng/core-perf.h

Purpose: public perf statistics types and API declarations, compiled only when perf support is available.

Important APIs/types: `STRESS_PERF_STATS`, `STRESS_PERF_INVALID`, `STRESS_PERF_MAX`, `stress_perf_stat_t`, `stress_perf_t`, and declarations for perf open/enable/disable/close/dump/init.

Control flow: preprocessor gates the entire API on pthread, Linux perf header, and `__NR_perf_event_open`.

State/persistence: `stress_perf_t` is caller-owned per stressor instance and stores file descriptors plus final counters.

Dependencies/integration: included by stats structures and `core-perf.c`; requires Linux perf build features and stress-ng list/stat types.

Risks: code using perf APIs must be inside the same `STRESS_PERF_STATS` guard; `STRESS_PERF_MAX` must cover the implementation table size.

Test signals: compile with and without perf support, validate structure initialization, and assert event table size stays below `STRESS_PERF_MAX`.
