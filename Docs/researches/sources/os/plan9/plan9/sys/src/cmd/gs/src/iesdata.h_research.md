# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iesdata.h

Defines the execution stack data structure.

Key points:
- Includes `isdata.h`.
- Defines `exec_stack_t` with the actual `ref_stack_t stack` and a cached `ref *current_file`.
- `current_file` points to the topmost executable file on the execution stack, or null.
- Comments document the cache invariant and require stack push/pop code to clear or check the cache when executable files may be involved.
- Provides `public_st_exec_stack()` descriptor macro using `st_ref_stack` suffix storage metadata.
- Notes `current_file` is cleared by GC and is not declared as a traced pointer.

Research relevance:
- Small performance/data-integrity component for fast `currentfile` lookup in the interpreter.
