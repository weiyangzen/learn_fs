# sources/storage-engines/wiredtiger/test/cppsuite/src/component/statistics/statistics.cpp

Purpose: Implements the generic statistic bound checker used by metrics monitor.

Important APIs/types/functions: constructor reads `max`, `min`, `postrun`, `runtime`, and `save` from configuration. `check` reads a stat via `metrics_monitor::get_stat` and fails if outside min/max. `get_value` returns the current stat. Getters expose all configuration fields.

Control flow: metrics monitor decides when to call `check` and whether to save or postrun-validate based on the getter flags.

State and persistence: stores stat id, bounds, name, and mode flags in memory; no persistence.

Dependencies/integration: depends on configuration keys, logger, metrics monitor, and scoped cursor.

Risks and test signals: error text says post-run even for runtime checks, which can be diagnostically confusing. Any out-of-range value is fatal.
