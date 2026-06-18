# File Research: sources/os/linux/linux/io_uring/query.c

io_uring capability query implementation. This file serves linked user query headers and returns structured feature data for opcodes, zero-copy receive, and shared completion queue layout.

Key responsibilities:
- Implements `io_query()` for `IORING_REGISTER_QUERY`.
- Supports query operations for opcode/register/flag availability, zcrx capabilities, and shared CQ header layout.
- Walks a user-provided linked list of `io_uring_query_hdr` records.
- Copies bounded result structures back to userspace with per-entry status in `hdr.result`.

Important data flows:
- `io_handle_query_entry()` copies a header, clamps requested data size to `IO_MAX_QUERY_SIZE`, validates reserved fields, copies input query data, fills the selected result, then copies the result and updated header back.
- `io_query()` follows `hdr.next_entry` until NULL, with `IO_MAX_QUERY_ENTRIES` as a cycle/abuse guard.

Important invariants:
- `nr_args` must be zero for query registration.
- Reserved fields and preexisting `result` must be zero.
- Unknown query opcodes return `-EOPNOTSUPP` in the per-entry result, not as a syscall-level traversal failure.
