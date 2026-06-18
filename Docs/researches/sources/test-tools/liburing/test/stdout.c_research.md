# sources/test-tools/liburing/test/stdout.c

Purpose: checks writes to stdout and fixed-buffer writes to stdout/pipe through io_uring complete with correct byte counts and data.

Important APIs/types/functions: `io_uring_prep_writev`, `io_uring_prep_write_fixed`, `io_uring_prep_readv`, `io_uring_register_buffers`, `io_uring_unregister_buffers`, `STDOUT_FILENO`, pipes, and aligned buffers.

Control flow: `test_stdout_io()` submits a normal writev to stdout. `test_stdout_io_fixed()` registers one aligned buffer and writes it fixed to stdout. `test_pipe_io_fixed()` registers a fixed buffer, writes it to a pipe, concurrently reads from the pipe, and verifies both completions and read payload.

State/persistence behavior: stdout receives test text. Pipe data and registered buffer state are transient.

Dependencies/integration: depends on stdout being writable and fixed-buffer registration support.

Risks/test signals: detects stdout/pipe write errors, wrong byte counts, fixed-buffer registration failures, and pipe read payload mismatch.
