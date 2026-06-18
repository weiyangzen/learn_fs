# sources/storage-engines/rocksdb/util/async_file_reader.cc

Purpose: implements coroutine-gated asynchronous multi-read batching for RocksDB file reads when `USE_COROUTINES` is enabled. It queues suspended read awaiters, issues `RandomAccessFileReader::ReadAsync` calls for each `FSReadRequest`, polls the `FileSystem`, cleans I/O handles, records stats, and resumes suspended coroutines.

Important APIs and functions: `AsyncFileReader::MultiReadAsyncImpl(ReadAwaiter*)` appends an awaiter to an intrusive queue, increases `num_reqs_`, resizes per-request `io_handle_` and deleter vectors, and invokes `ReadAsync` with a callback that copies `status`, `result`, and `fs_scratch` back to the original `FSReadRequest`. `AsyncFileReader::Wait()` gathers non-null I/O handles from all queued awaiters, calls `fs_->Poll`, releases handles with per-request deleters, overwrites request statuses with poll errors when the request itself succeeded, resumes each coroutine, records `MULTIGET_IO_BATCH_SIZE`, and clears queue state.

Control flow and state: every `co_await` call suspends because `await_ready` is false and `MultiReadAsyncImpl` returns true. The reader owns a transient queue via `head_` and `tail_`, plus aggregate `num_reqs_`. The queue is drained in FIFO order by `Wait()`. There is no locking in this implementation; the friend `SingleThreadExecutor` integration implies single-threaded ownership.

Dependencies and integration: depends on `util/async_file_reader.h`, `FileSystem::Poll`, `RandomAccessFileReader::ReadAsync`, `StopWatch`, histograms, and `autovector`. Integration search shows `table/multiget_context.h` exposing an `AsyncFileReader` for MultiGet style table reads.

Risks and test signals: correctness depends on `Wait()` being called after scheduling; otherwise coroutines remain suspended and handles remain pending. If `ReadAsync` returns non-OK, the callback will not run and the code stores the error directly, but no handle may be present. Poll errors are broadcast to requests that have not already failed. The compile-time `USE_COROUTINES` guard means builds without coroutine support do not test this code. No direct test appears in this subset.
