# sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_write2_latency.cc

## Purpose
This latency test measures FSAL write2/write behavior for small, large, stable, unstable, and bypass write paths. It writes to one open file under `write2_latency`.

## Important APIs, Types, And Functions
`Write2EmptyLatencyTest` allocates FSAL share state, opens `test_file` with `open2`, closes it with `close2`, and removes it. Tests allocate `struct fsal_io_arg` with a single `iovec`, populate `async_process_data`, and call `fsal_write` on either the MDCACHE handle or `mdcdb_get_sub_handle(test_file)`.

## Control Flow, State, And Persistence
Single-call tests cover 64-byte unstable, 64-byte stable, 2 MiB unstable, and 2 MiB stable writes. Loop tests write 64-byte buffers one million times while advancing the offset by 64 bytes, producing a large sparse or contiguous file depending on backend behavior. Teardown removes the file after close and state free.

## Dependencies And Integration Points
The file integrates FSAL I/O argument conventions, asynchronous process data with pthread condition/mutex pointers, MDCACHE bypass access, and shared Ganesha environment setup. Stable write behavior depends on the FSAL honoring `fsal_stable`.

## Risks And Test Signals
The test does not read data back, so it measures write success rather than persistence correctness. Large and loop tests can generate significant storage I/O. As with read tests, it initializes async completion state but does not explicitly wait for callbacks, relying on synchronous invocation. Success status and teardown are the key signals.
