<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/write/write06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/write/write06.c

Purpose: focused `write(2)` syscall test that verifies `O_APPEND` atomically appends at EOF even after seeking to an earlier offset, producing 3 KiB size and offset.

Important APIs/types/functions: uses LTP safe open/read/write/close/seek wrappers and the modern `tst_test` harness. The exact fixture varies by file: regular temp file, protected mmap page, FIFO, pipe, signal handler, or append-mode file.

Control flow/state: setup creates the required descriptor state, `verify_write()` performs the single syscall scenario, and cleanup closes descriptors/unlinks files. Persistent state is confined to the LTP tmpdir and, for append/corruption tests, file content and offset are part of the assertion.

Dependencies/integration: depends on Linux/POSIX file descriptor semantics, LTP tmpdir isolation, and for negative tests exact errno propagation. The append test uses LTP allocated buffers through `.bufs`.

Risks/test signals: failures identify short writes where full writes are expected, wrong errno, missing SIGPIPE, data corruption after a failed write, FIFO capacity behavior changes, or broken `O_APPEND` offset/size semantics.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/write/write06.c -->
