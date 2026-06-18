# sources/storage-engines/wiredtiger/test/cppsuite/src/component/statistics/statistics.h

Purpose: Declares the base class for metric/statistic validation.

Important APIs/types/functions: `statistics` has constructors, virtual `check`, virtual `get_value`, and getters for stat field, min/max, name, and mode flags.

Control flow: subclasses may override `check` and `get_value` for derived metrics while preserving the base config contract.

State and persistence: protected fields hold all checker state.

Dependencies/integration: included by metrics monitor and specialized statistic classes.

Risks and test signals: base class assumes integer stat values and fixed min/max bounds; tests needing non-integer or multi-field semantics require subclassing.
