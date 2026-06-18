# sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_read2_latency.cc

## Purpose
This GoogleTest executable measures and sanity-checks FSAL read2/read latency through Ganesha's FSAL object API. It creates a per-test directory named `read2_latency`, opens one regular file with `open2`, writes data through `fsal_write`, then reads the same bytes through `fsal_read`. It compares normal MDCACHE-backed handles with direct sub-handles returned by `mdcdb_get_sub_handle`.

## Important APIs, Types, And Functions
The fixture `Read2EmptyLatencyTest` derives from `gtest::GaneshaFSALBaseTest`, uses `op_ctx->fsal_export->exp_ops.alloc_state` to allocate a `STATE_TYPE_SHARE`, opens `TEST_FILE` with `obj_ops->open2`, and closes it with `obj_ops->close2`. Test bodies allocate `struct fsal_io_arg` plus one `iovec` on the stack via `alloca`, initialize `struct async_process_data`, and call `fsal_write` and `fsal_read`. Timing uses `now` and `timespec_diff`.

## Control Flow, State, And Persistence
`SetUp` starts from the shared environment's export root and creates an opened file object under the per-test root. `TearDown` closes the state, frees it, removes the file, releases the object reference, and delegates root cleanup to the base fixture. `SIMPLE` and `LARGE_DATA_READ` verify returned bytes with `memcmp`; loop tests write a large backing buffer once and then read 64-byte slices while advancing `read_arg->offset`. The tests persist only transient filesystem objects in the configured export and remove them afterward.

## Dependencies And Integration Points
The file depends on Ganesha FSAL headers, `common_utils.h`, MDCACHE debug helpers, Boost program options, pthread condition/mutex primitives for async I/O, and `gtest.hh` for environment setup. Its `main` parses config/log/debug/export/session/event-list/profile flags and registers `gtest::Environment` with `TEST_ROOT`.

## Risks And Test Signals
`LOOP_COUNT` is one million and the loop setup can allocate or write tens of megabytes, so runtime and backend storage behavior matter. `io_data.done` is initialized but not waited on, relying on synchronous behavior from `fsal_read`/`fsal_write` when called with `true`. The bypass cases explicitly skip MDCACHE and can diverge from normal behavior. The strongest correctness signal is byte comparison in normal read paths; bypass tests only assert success.
