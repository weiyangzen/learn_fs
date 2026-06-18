# File Research: sources/local-fs/dlm/dlm_sand/list.h

This is an older/smaller userspace copy of Linux intrusive doubly linked list helpers for `dlm_sand`.

Provided functionality:
- `container_of`, poison pointers, and `struct list_head`.
- Initialization and declaration macros.
- Add/delete/move operations: `list_add`, `list_add_tail`, `list_del`, `list_del_init`, `list_move`, `list_move_tail`.
- Empty checks: `list_empty`, `list_empty_careful`.
- Splice helpers: `list_splice`, `list_splice_init`.
- Entry and iteration macros: `list_entry`, `list_first_entry`, raw iteration, reverse iteration, safe iteration, typed entry iteration, typed reverse iteration, continuation, and typed safe iteration.

Differences from `dlm_controld/list.h`:
- It does not use `READ_ONCE`/`WRITE_ONCE`.
- It has fewer helper macros and no debug validation stubs.
- It defines its own `container_of` without the stronger static type assertion used by `linux_helpers.h`.

Used by:
- `dlm_sand` structures via `sand_internal.h` and related source files.
