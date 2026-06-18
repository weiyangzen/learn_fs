# sources/test-tools/syzkaller/tools/syz-declextract/testdata/io_uring.c

Purpose: this fixture tests extraction of io_uring operation tables from indexed const arrays.

Important APIs and flow: defines `struct io_issue_def` with `prep` and `issue` function pointers, simple prep/issue functions for nop/read/write, and an `ops[]` table indexed by `IORING_OP_*`. Supported entries map NOP to `io_nop`, READV to `io_read`, and WRITEV to `io_write`; `IORING_OP_NOT_SUPPORTED` uses an unsupported prep sentinel but an issue function that should not become a supported operation.

State and persistence: static table only.

Dependencies and integration: includes UAPI `io_uring.h`; paired JSON feeds declextract tests for `iouring_ops`.

Risks: fixture only models one table shape and simple function names.

Test signals: generated JSON should include functions, four opcode constants, and three supported `iouring_ops` records.
