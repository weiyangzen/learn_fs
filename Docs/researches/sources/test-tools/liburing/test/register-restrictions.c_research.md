# sources/test-tools/liburing/test/register-restrictions.c

Purpose: validates io_uring restriction registration on disabled rings. It tests allowed SQE opcodes, allowed register opcodes, required fixed-file flags, allowed/required SQE flags, empty restriction sets, and rejection of restriction registration or submission in invalid ring states.

Important APIs and types: `struct io_uring_restriction`, restriction opcodes `IORING_RESTRICTION_SQE_OP`, `IORING_RESTRICTION_REGISTER_OP`, `IORING_RESTRICTION_SQE_FLAGS_ALLOWED`, `IORING_RESTRICTION_SQE_FLAGS_REQUIRED`, `io_uring_register_restrictions`, `io_uring_enable_rings`, `IORING_SETUP_R_DISABLED`, `IOSQE_FIXED_FILE`, `IOSQE_ASYNC`, `IOSQE_IO_LINK`, `IOSQE_IO_DRAIN`, file registration, and read/writev SQEs.

Control flow: `test_restrictions_sqe_op()` allows `WRITEV` and `WRITE`, then verifies `WRITEV` succeeds and `READV` gets `-EACCES`. `test_restrictions_register_op()` allows only buffer registration and requires file registration to fail. `test_restrictions_fixed_file()` allows read/writev plus file registration and requires `IOSQE_FIXED_FILE`; fixed-file read/write succeed while non-fixed write fails. `test_restrictions_flags()` permits only fixed-file SQEs with optional ASYNC or IO_LINK; IO_DRAIN, ASYNC without fixed file, and no flags fail. `test_restrictions_empty()` registers zero restrictions, causing all tested register and SQE operations to be denied. `test_restrictions_rings_not_disabled()` requires restriction registration on an enabled ring to return `-EBADFD`; `test_restrictions_rings_disabled()` requires submission before enabling to return `-EBADFD`.

State and persistence: each test owns a fresh ring and pipe. Restrictions persist after registration and before/after enabling, defining the authorization policy for later operations.

Dependencies and integration: restriction support may be absent and is skipped on `-EINVAL`. Tests depend on disabled-ring setup and pipe I/O.

Risks and test signals: wrong `-EACCES` or `-EBADFD` behavior, allowed disallowed operations, denied allowed operations, or enable failures indicate security-policy regressions. Passing confirms restrictions are enforced consistently for SQEs, flags, and register operations.
