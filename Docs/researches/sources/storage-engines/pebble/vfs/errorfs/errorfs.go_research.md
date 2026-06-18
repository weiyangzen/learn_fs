<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/errorfs/errorfs.go -->
# sources/storage-engines/pebble/vfs/errorfs/errorfs.go

## Purpose
Implements a `vfs.FS` and `vfs.File` wrapper that injects artificial errors before filesystem operations. It is a test utility for forcing Pebble code through rare IO error paths without modifying production VFS implementations.

## Important APIs, Types, and Functions
`ErrInjected` is the default labelled error. `Op`, `OpKind`, `OpKinds`, `ReadOps`, and `WriteOps` classify VFS and file operations. `OnIndex`, `Injector`, `InjectorFunc`, `Any`, `Counter`, and `Toggle` compose injection behavior. `Wrap` wraps an FS, and `WrapFile` wraps a single file. `FS` implements `vfs.FS`; `errorFile` implements `vfs.File`.

## Control Flow
Every wrapped FS method constructs an `Op` and calls `inj.MaybeError` before delegating to the underlying FS. Methods that return opened files wrap those files with `errorFile` so subsequent reads, writes, stats, syncs, and preallocations are also injectable. `Any` scans injectors in order and returns the first error. `Counter` records injected count and last error under a mutex, and `Toggle` gates an injector through an atomic boolean.

## State and Persistence Behavior
The wrapper does not persist state or alter the underlying filesystem when injection fires; it returns the injected error before the delegated operation runs. `Counter` stores counters in memory, and `Toggle` stores the enabled flag atomically. File close intentionally does not inject errors because close failures are not expected in Pebble's modeled error paths.

## Dependencies and Integration Points
Integrates with `vfs.FS`/`vfs.File`, the DSL predicates in `dsl.go`, and the generic `internal/dsl.OnIndex` implementation. WAL failover tests and other Pebble tests wrap `vfs.NewMem` or disk-backed VFSs to exercise IO failure handling.

## Risks and Edge Cases
`OpFileClose` is classified as a write op but `errorFile.Close` bypasses injection, so close-error testing must use other wrappers. `Prefetch` also does not inject errors. For two-path operations like link and rename, the source path is used for predicate matching, which can surprise tests that want to target the destination path. The `init` invariant panics if new op kinds are added without updating read/write classification.

## Test Signals
`errorfs_test.go` covers DSL parsing. Broader integration is visible in `failover_manager_test.go` and `failover_writer_test.go`, where injected create/write/sync/open-dir errors drive failover and close paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/errorfs/errorfs.go -->
