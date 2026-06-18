# sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/impl.py

## Purpose
This is a vendored FoundationDB Python binding implemented with `ctypes` over `libfdb_c`. It loads the client library, initializes the C API, starts/stops the network thread, exposes database/transaction/future abstractions, implements transactional retry wrappers, and dynamically attaches options, predicates, enums, and atomic mutation methods.

## Important APIs, Types, And Functions
Dynamic method generation is handled by `fill_options`, `make_enum`, and `fill_operations` using `fdboptions.py`. `transactional` wraps functions so calls with a `Database` create a transaction, retry on `FDBError` through `on_error`, commit, and return the function result; calls with an existing `TransactionRead` compose without committing.

Core types include `FDBError`, `FDBRange`, `TransactionRead`, `Transaction`, `Future` and specialized futures (`FutureVoid`, `FutureInt64`, `FutureKeyValueArray`, `FutureKeyArray`, `FutureStringArray`, `FutureString`, `Value`, `Key`), `_TransactionCreator`, `Database`, `Cluster`, `KeySelector`, and `KeyValue`. Public open/init helpers are `init`, `open`, `open_v609`, `open_v13`, `create_database`, `create_cluster`, and `strinc`.

`init_c_api()` declares C function signatures and error checking for network, future, database, tenant compatibility shims, transaction reads/writes, watches, conflict ranges, approximate size, versionstamps, and range split APIs.

## Control Flow
At import, the module selects a platform-specific library name, tries a colocated library, a `.pth` pointer, then dynamic loader lookup, and assigns it to `_FDBBase.capi`. Dynamic option and mutation methods are installed. Callers select an API version outside this file, then `open()` initializes the network if needed, caches a `Database` by cluster file, and returns it.

Transactions flow through `Database.create_transaction()` to a `Transaction` sharing one C pointer with its snapshot `TransactionRead`. Reads return futures or `FDBRange` iterators. `FDBRange` eagerly dispatches the first range read and lazily requests additional batches using key selectors. Mutations call direct C API methods and commits return `FutureVoid`.

Futures block in Python using callbacks and per-thread semaphores rather than native blocking, so Python signals can still be handled. Optional event models replace blocking behavior for gevent, debug polling, or asyncio.

## State And Persistence Behavior
Persistent database changes happen only through transaction mutations: `set`, `clear`, `clear_range`, atomic ops, conflict range operations, watches, commits, and versionstamp operations. Module-level runtime state includes the global network thread, `open_databases` cache, callback pinning state, and a thread-local semaphore. `open()` reuses database handles for each cluster file; `_stop_on_exit` stops the global network and joins the thread.

The wrapper enforces bytes-only keys/values through `keyToBytes` and `valueToBytes`, while option parameters may encode strings to UTF-8. Snapshot reads share the transaction pointer but set the snapshot flag in C API calls.

## Dependencies And Integration Points
This file depends on a 64-bit Python runtime, `ctypes`, `fdb.tuple`, `fdboptions`, and a compatible `libfdb_c`. Metadata audit tools depend on `fdb.api_version`, `fdb.open`, `fdb.transactional`, transaction option helpers, and system-key access exposed here. It also integrates with asyncio/gevent by monkey-patching future behavior and `_TransactionCreator` methods.

## Risks And Edge Cases
The binding is tightly coupled to C API symbol availability and exact signatures; a mismatched client library can fail at import or behave incorrectly. `Database.open_tenant` is a temporary compatibility shim that returns `None`, so tenant callers cannot rely on it. `transactional` may rerun user code multiple times, making side effects outside FDB unsafe. `open_databases` never evicts handles. The destructor-based cleanup of C objects depends on Python GC timing. Async code references `asyncio` only after event-model setup.

## Test Signals
Strong tests load a known `libfdb_c`, set an API version, open a test cluster, execute get/set/clear/range operations, verify retry behavior through injected retryable errors, and validate future callbacks and `wait_for_any`. Compatibility tests should exercise system-key options used by metadata tools, `strinc`, dynamic option/mutation method presence, and import failure paths for missing libraries.
