# sources/test-tools/liburing/test/ring-query.c

Purpose: validates the `IORING_REGISTER_QUERY` ABI for opcode/capability discovery, including invalid inputs, linked query headers, loop rejection, and forward/backward compatible result sizes.

Important APIs/types/functions: `io_uring_register`, `IORING_REGISTER_QUERY`, `IO_URING_QUERY_OPCODES`, `struct io_uring_query_hdr`, `struct io_uring_query_opcode`, short/large local ABI shape variants, and `uring_ptr_to_u64`.

Control flow: `test_basic_query()` probes support and stores the system opcode counts/flags. `test_invalid()` checks unsupported query ops and bad pointers. `test_chain()` links three valid query headers and verifies identical outputs. `test_chain_loop()` ensures cyclic query lists fail. Compatibility tests pass shorter and larger output buffers and compare common fields with `sys_ops`.

State/persistence behavior: no persistent state; `sys_ops` is process-global cached query output used to validate subsequent tests.

Dependencies/integration: includes `test.h` and liburing helpers, but uses the register ABI directly. It deliberately supports a null ring pointer by registering against fd `-1` for global query behavior.

Risks/test signals: exact negative errno behavior matters (`-EOPNOTSUPP`, `-EFAULT`, nonzero loop failure). A kernel that changes query sizing or result fields could fail compatibility checks.
