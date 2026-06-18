<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/futures.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/futures.go

Purpose: wraps FoundationDB C futures in Go interfaces and typed future implementations.

Important APIs: `Future`, `FutureByteSlice`, `FutureKey`, `FutureNil`, `FutureKeyArray`, `FutureInt64`, `FutureStringSlice`, plus internal `future`, `newFuture`, `BlockUntilReady`, `IsReady`, `Cancel`, and C callback bridge `go_set_callback`.

Control flow: C futures are wrapped with finalizers that destroy them. Blocking uses a mutex passed to a C callback that unlocks when ready. Typed `Get` methods block, call the appropriate `fdb_future_get_*`, copy C memory into Go values, and convert C errors to `Error`. Byte/key futures use `sync.Once` to cache results; others fetch on each `Get`.

State and persistence: no database persistence. Runtime state includes C future pointers, parent db/transaction references to keep owners alive, cached values/errors, and finalizers.

Dependencies and integration: cgo links `fdb_c` and math library. Used by transaction/database/locality APIs. `runtime.KeepAlive` prevents premature finalization.

Risks: C struct layout assumptions in `stringRefToSlice` and array pointer arithmetic are ABI-sensitive. Some futures do not call `fdb_future_release_memory`, which should be checked against C API ownership rules. Finalizers make cleanup nondeterministic; explicit cancel can still leave resources until GC. Callback/mutex pattern must avoid deadlocks if future callback behavior changes.

Test signals: indirectly exercised by transaction/range/versionstamp tests; no focused future lifecycle or cancellation tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/futures.go -->
