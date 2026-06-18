<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/include/liburing/io_uring/query.h -->
## sources/test-tools/liburing/src/include/liburing/io_uring/query.h

Purpose: defines query UAPI structures used with `IORING_REGISTER_QUERY` for probing aspects of io_uring support and configuration without a specific ring fd.

Important APIs/types/functions: `io_uring_query_hdr` is the common header with query type, flags, item count, and item pointer. Query types include opcode, zero-copy receive, and send-completion-queue queries. `io_uring_query_opcode` reports opcode support and command-specific flags; `io_uring_query_zcrx` and `io_uring_query_scq` report feature masks.

Control flow: userspace fills a header with one query type and pointer to an array of items; `register.c` invokes `__sys_io_uring_register(-1, IORING_REGISTER_QUERY, query, 0)`.

State and persistence behavior: no local persistence. Results are written back into the provided query item buffers.

Dependencies and integration points: included by `liburing.h`; its public wrapper is `io_uring_register_query`. Values must align with kernel UAPI support.

Risks: query buffers and `nr` must match the requested type. As an evolving UAPI, unknown flags or item layouts need conservative handling by callers.

Test signals: no direct listed test, but query support can be validated through feature-probing tests in the wider suite.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/include/liburing/io_uring/query.h -->
