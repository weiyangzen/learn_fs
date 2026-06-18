<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/errors.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/errors.go

Purpose: defines the Go wrapper for low-level FoundationDB C API errors.

Important APIs: `Error{Code int}`, `Error.Error()`, and `Error.Is(target error)`. `Error()` calls `fdb_get_error` through cgo to include the C library message. `Is` matches both value and pointer `Error` targets with equal codes.

Control flow: any C API function returning nonzero `fdb_error_t` is wrapped as `Error{int(err)}` by surrounding files. Panic recovery in `panicToError` also recognizes this concrete type.

State and persistence: no persistent state. Error text is fetched from the linked C library at call time.

Dependencies and integration: cgo includes `foundationdb/fdb_c.h` with `FDB_API_VERSION 800`; generated sentinels depend on this type. `go:generate` points to `internal/gen_errors/main.go`.

Risks: `panicToError` only catches value `Error`, not `*Error`; this matches current `MustGet` panics but is a trap if future code panics pointers. `Error()` depends on the C library being loadable and initialized enough for message lookup. Code values must remain compatible with linked FoundationDB client versions.

Test signals: `errors_test.go` exercises wrapping and `errors.Is` matching for value/pointer targets and wrapped values.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/errors.go -->
