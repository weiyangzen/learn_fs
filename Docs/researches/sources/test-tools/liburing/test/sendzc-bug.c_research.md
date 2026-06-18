# sources/test-tools/liburing/test/sendzc-bug.c

Purpose: regression for zero-copy sendmsg fixed-buffer lifetime where imported buffer nodes must remain tied to notification lifetime, not just the main request.

Important APIs/types/functions: `io_uring_prep_sendmsg_zc`, `IORING_RECVSEND_FIXED_BUF`, `io_uring_register_buffers`, `io_uring_unregister_buffers`, `SO_ZEROCOPY`, `mmap`, `munmap`, and a local TCP socketpair helper.

Control flow: creates a connected TCP pair, enables `SO_ZEROCOPY`, registers a 1 MiB mapped buffer, submits fixed-buffer `sendmsg_zc`, waits for the main CQE, unregisters and unmaps the buffer immediately, then reads the data from the peer socket.

State/persistence behavior: memory lifetime is the core state: the userspace buffer is unmapped after the send completion but before notification lifetime may end. Socket data is read into a static buffer.

Dependencies/integration: depends on TCP loopback, zero-copy sendmsg support, fixed buffer registration, and kernel notification ownership semantics. `-EINVAL` from the CQE is treated as skip.

Risks/test signals: a buggy kernel can access freed/unmapped memory, crash, or corrupt send data. The test mainly checks survival and successful peer read.
