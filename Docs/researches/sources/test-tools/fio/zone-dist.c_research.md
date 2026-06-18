# sources/test-tools/fio/zone-dist.c

Purpose: precomputes lookup tables for fio zone split distributions so hot IO paths can map access percentages to size ranges quickly.

Important APIs/functions: `td_zone_gen_index(td)` checks whether any direction has zone splits, allocates `td->zone_state_index`, and builds 100-entry indexes per direction. `td_zone_free_index(td)` frees every direction index and clears pointers. Internal `__td_zone_gen_index()` expands each configured `zone_split` entry across its access-percentage range with cumulative size percentages and byte sizes. `has_zones()` checks configured split counts across read/write/trim directions.

Control flow/state: for each direction, cumulative previous size/access counters are advanced across configured split entries; each access-percent bucket records current and previous cumulative size boundaries.

Dependencies/integration: depends on `thread_data`, `thread_options.zone_split_nr`, `zone_split`, `zone_split_index`, and `DDIR_RWDIR_CNT` from fio core headers.

Risks/test signals: allocation assumes exactly 100 percentage buckets and does not check `malloc()` failure. Misconfigured access percentages not summing to 100 can leave uninitialized buckets or overrun. Tests should cover no splits, exact 100, under/over totals, and freeing after partial allocation.
