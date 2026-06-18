# sources/test-tools/stress-ng/core-cpuidle.h

Purpose: C-state data structure and cpuidle API declarations.

Important APIs and control flow: defines linked-list node `cpu_cstate_t` and exposes init/free/log/head/read/dump functions.

State and persistence: no header-owned state; implementation owns global list.

Dependencies and integration: uses `stress_cstate_stats_t`, `stress_list_item_t`, and `FILE` from stress-ng headers.

Risks and test signals: callers must initialize before reading/dumping and free at shutdown. Signal is correct lifecycle use in stress-ng metrics paths.
