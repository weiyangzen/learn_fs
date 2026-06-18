# sources/storage-engines/foundationdb/bindings/ruby/lib/fdbimpl.rb

Purpose: This is the main Ruby FFI implementation for FoundationDB. It loads `libfdb_c`, attaches C API functions, runs the network thread, exposes database/transaction/future abstractions, and dynamically defines options and mutations.

Important APIs and types: It defines module `FDB::FDBC`, `Error`, `Future`, `FutureNil`, `LazyFuture`, `LazyString`, `Int64Future`, `FutureKeyValueArray`, `FutureKeyArray`, `FutureStringArray`, `Database`, `TransactionRead`, `Transaction`, `KeySelector`, `KeyValue`, option classes, `FDB.open`, `FDB.options`, `FDB.stop`, `FDB.key_to_bytes`, `FDB.value_to_bytes`, and `FDB.strinc`.

Control flow: `FDBC` validates CPU/OS, loads the native client library, and attaches functions in `init_c_api`. Option classes and mutation methods are generated from `fdboptions.rb`. `FDB.open` lazily starts the network thread and caches databases by cluster file. `Database#transact` retries a yielded transaction until commit succeeds or `on_error` handles retry. Range reads use an enumerable that fetches additional batches based on `more`, limit, and reverse state.

State and persistence behavior: Runtime state includes callback arrays, network thread monitor, open database cache, native pointer finalizers, and lazy future values. Persistent state is only affected through C API database operations. Finalizers destroy native database/future/transaction pointers.

Dependencies and integration points: It depends on the `ffi` gem, generated `fdboptions`, Ruby threading/monitor primitives, native `libfdb_c`, and entrypoint version selection from `fdb.rb`. Tuple, locality, directory, and tester code build on it.

Risks: FFI signatures, pointer ownership, finalizer timing, and callback lifetime are critical. `FutureKeyArray#wait` appears to allocate `ks` but calls `fdb_future_get_key_array` with `kvs`, a likely bug if this path is exercised. Network startup must avoid races between setup and run. The database cache keying and finalizers are process-local.

Test signals: Ruby tester operations cover reads/writes/ranges, atomic ops, futures, watches, options, transaction retry, locality, directory layer, and API-version guards.
