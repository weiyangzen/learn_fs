# File Research: sources/os/linux/linux/io_uring/opdef.h

Header defining opcode metadata structures.

Key contents:
- `struct io_issue_def` describes hot-path operation behavior and function pointers used by submission/issue code.
- `struct io_cold_def` stores operation name plus optional SQE-copy, cleanup, and failure callbacks.
- Declares `io_issue_defs[]`, `io_cold_defs[]`, opcode support query, and optable init.

This header is included by the core engine and operation modules that need to inspect opcode properties.
