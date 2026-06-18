# sources/storage-engines/rocksdb/util/async_file_reader.h

Purpose: declares `AsyncFileReader`, an awaitable facade for batching asynchronous `RandomAccessFileReader` reads under coroutine builds. It lets callers request a multi-read operation and later run it through `folly::coro::co_viaIfAsync`.

Important APIs and types: `AsyncFileReader(FileSystem*, Statistics*)` stores non-owning pointers. `MultiReadAsync(RandomAccessFileReader*, const IOOptions&, FSReadRequest*, size_t, IODebugContext*)` returns `ReadOperation<ReadAwaiter>`. `ReadAwaiter` implements `await_ready`, `await_suspend`, and `await_resume`, captures read parameters, keeps `autovector<void*,32>` handles and `autovector<IOHandleDeleter,32>` deleters, stores the awaiting coroutine handle, and has an intrusive `next_` pointer. `ReadOperation::viaIfAsync` wraps the awaiter in Folly's executor-aware coroutine scheduling.

Control flow and state: callers receive a deferred `ReadOperation`. When awaited, `ReadAwaiter::await_suspend` caches the coroutine handle and calls `MultiReadAsyncImpl`; the implementation queues it and returns true, so the coroutine suspends. `Wait()` later polls and resumes. `head_`, `tail_`, and `num_reqs_` track pending operations.

Dependencies and integration: includes `file/random_access_file_reader.h`, Folly coroutine support, RocksDB file-system and statistics APIs, `autovector`, and `stop_watch`. `SingleThreadExecutor` is a friend and is expected to drive `Wait()`. `MultiGetContext` is a visible consumer.

Risks and test signals: the header has a malformed comment/pragma line followed by a second `#pragma once`; compilers tolerate this as comment text plus the real pragma, but it is untidy. Lifetimes of `file`, `opts`, `read_reqs`, and `dbg` must outlive suspension. There is no synchronization, so multi-threaded use would race on queue state. No direct tests are included here; coverage depends on coroutine-enabled read paths.
