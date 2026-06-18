# sources/test-tools/liburing/test/short-read.c

Purpose: verifies a readv larger than the file returns a short successful completion rather than an error or hang.

Important APIs/types/functions: `t_create_file`, `io_uring_prep_readv`, `io_uring_wait_cqes`, `struct iovec`, `BUF_SIZE`, and `FILE_SIZE`.

Control flow: creates a 1024-byte temporary file, unlinks it after open, allocates a 4096-byte buffer, queues one `readv`, waits for one CQE, and expects `cqe->res == FILE_SIZE`.

State/persistence behavior: creates `.short-read` transiently and removes it immediately after open. Read state is a single fd and heap buffer.

Dependencies/integration: uses normal filesystem reads and liburing queue setup. No feature probing is needed beyond ring init.

Risks/test signals: failure indicates incorrect short-read result, wait failure, SQE acquisition failure, or submit count mismatch.
