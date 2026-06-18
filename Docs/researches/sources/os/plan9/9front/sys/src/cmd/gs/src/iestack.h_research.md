# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iestack.h

Defines the execution stack API aliases and cache helpers.

Key points:
- Includes `iesdata.h` and `istack.h`.
- Defines `es_ptr` and `const_es_ptr` as execution-stack pointer aliases.
- Provides macros:
  - `estack_clear_cache(pes)`
  - `estack_set_cache(pes, pref)`
  - `estack_check_cache(pes)`
- `estack_check_cache` caches the top stack entry if it is an executable file ref.

Dependencies and interactions:
- Operates on `exec_stack_t.current_file`.
- Relies on ref type/attribute predicates such as `r_has_type_attrs`.

Research relevance:
- Supports fast `currentfile` behavior and documents the coupling between execution-stack mutation and cache correctness.
