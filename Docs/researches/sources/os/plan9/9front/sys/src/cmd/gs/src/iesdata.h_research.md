# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iesdata.h

Defines the execution stack data structure.

Key points:
- Includes `isdata.h`.
- Defines `exec_stack_t` containing:
  - `ref_stack_t stack`
  - cached `ref *current_file`
- The `current_file` cache points to the topmost executable file on the execution stack, or is null.
- Comments define cache invariants and require stack push/pop code to clear/check the cache when executable files may be involved.
- Provides `public_st_exec_stack()` descriptor macro using `st_ref_stack` as suffix storage metadata.
- Notes that `current_file` is cleared by GC and therefore not declared as a traced pointer.

Dependencies and interactions:
- `iestack.h` provides cache manipulation macros around this data.
- Interpreter execution uses this to accelerate `currentfile` lookups.

Research relevance:
- Small but important performance/data-integrity component for Ghostscript’s execution stack.
