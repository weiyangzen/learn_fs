# sources/test-tools/strace/bundled/linux/include/uapi/linux/io_uring/query.h

Purpose: defines the `IORING_REGISTER_QUERY` payload ABI for discovering supported io_uring capabilities, including opcode coverage, zcrx support, and shared CQ/SQ ring geometry.

Important APIs/types/functions: `struct io_uring_query_hdr` is the common entry header with `next_entry`, `query_data`, `query_op`, `size`, and `result`. Query payloads include `io_uring_query_opcode`, `io_uring_query_zcrx`, and `io_uring_query_scq`.

Control flow: userspace chains or points query headers at payload buffers, selects `IO_URING_QUERY_OPCODES`, `IO_URING_QUERY_ZCRX`, or `IO_URING_QUERY_SCQ`, and submits via the register API. The kernel fills capability bitmasks, counts, alignment, size, and result status.

State/persistence behavior: queries are observational and should not mutate ring state. Results reflect kernel and possibly ring-supported capability state at call time.

Dependencies/integration: depends only on `linux/types.h` but is referenced from `io_uring.h` register op comments. strace should decode this as a register subcommand with nested payload selected by `query_op`.

Risks and test signals: the header is versioned through size/reserved fields and uses pointer-like `__u64` fields. Tests should verify chained query decoding, unsupported query result handling, and zcrx/scq alignment fields.
