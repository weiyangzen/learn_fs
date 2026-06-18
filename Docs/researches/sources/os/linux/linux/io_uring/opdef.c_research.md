# File Research: sources/os/linux/linux/io_uring/opdef.c

Opcode definition table for io_uring.

Key contents:
- `io_issue_defs[]` maps every `IORING_OP_*` to capability flags, async-data size, BPF filter payload sizing/population, prep function, and issue function.
- Capability flags drive core behavior: file requirement, plug eligibility, ioprio support, iopoll support, buffer selection, regular-file hashing, unbound non-regular io-wq placement, poll direction, audit skipping, vectorization, and 128-byte SQE use.
- Conditional entries return `-EOPNOTSUPP` prep stubs when kernel config lacks NET, EPOLL, or FUTEX support.
- `io_cold_defs[]` maps opcodes to names and cold-path callbacks for SQE copy, cleanup, and fail handling.
- `io_uring_get_opcode()` returns names for tracing/debugging.
- `io_uring_op_supported()` checks whether an opcode has real support in this build.
- `io_uring_optable_init()` validates table sizes, required prep/issue pointers, and names at init.

The table is the central contract between generic submission logic and per-opcode modules.
