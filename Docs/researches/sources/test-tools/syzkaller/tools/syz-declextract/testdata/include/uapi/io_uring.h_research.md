# sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/uapi/io_uring.h

Purpose: this UAPI fixture defines a small `enum io_uring_op` for io_uring operation-table extraction.

Important APIs and flow: enum values are `IORING_OP_NOP`, `IORING_OP_READV`, `IORING_OP_WRITEV`, and `IORING_OP_NOT_SUPPORTED`.

State and persistence: static enum only.

Dependencies and integration: included by `io_uring.c`, where an indexed `ops[]` table maps operation constants to prep/issue callbacks. The extractor should retain supported issue ops and skip not-supported sentinel behavior.

Risks: minimal enum does not model the real io_uring opcode space or aliases.

Test signals: paired JSON should expose four constants and three generated `iouring_ops` mappings.
