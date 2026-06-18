# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iestack.h

Defines execution-stack pointer aliases and current-file cache helpers.

Key points:
- Includes `iesdata.h` and `istack.h`.
- Defines `es_ptr` and `const_es_ptr`.
- Provides:
  - `estack_clear_cache(pes)`
  - `estack_set_cache(pes, pref)`
  - `estack_check_cache(pes)`
- `estack_check_cache` caches the top stack entry if it is an executable file ref.

Research relevance:
- Documents and enforces the coupling between execution-stack mutation and `currentfile` cache correctness.
