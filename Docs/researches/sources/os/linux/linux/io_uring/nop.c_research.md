# File Research: sources/os/linux/linux/io_uring/nop.c

Implements `IORING_OP_NOP` and `IORING_OP_NOP128`.

Behavior:
- Prep validates NOP-specific flags and can inject a result, request normal/fixed file lookup, request fixed-buffer lookup, force task-work completion, or provide CQE32 extra fields.
- Issue optionally resolves a file, resolves a fixed buffer node, sets failure on lookup errors, emits normal or 32-byte CQE result, and can complete through task_work with `IOU_ISSUE_SKIP_COMPLETE`.

NOP is used for testing and feature exercise paths, not just a zero-result no-op.
