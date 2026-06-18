# sources/storage-engines/foundationdb/bindings/go/src/_stacktester/directory.go

## Purpose

This file adds directory-layer instructions to the Go stack tester. It translates generated `DIRECTORY_*` operations into calls against the Go `fdb/directory` and `fdb/subspace` APIs, while preserving the stack tester’s index-based object model and error behavior for cross-binding comparison.

## Important APIs, Types, and Functions

`popTuples`, `tupleToPath`, and `tuplePackStrings` bridge stack values and directory path representations. `DirectoryExtension` stores a heterogeneous list of directory and subspace objects, plus the current index and an error fallback index. `newDirectoryExtension` seeds the list with `directory.Root()`. `cwd` returns the current `directory.Directory`; `css` returns the current `subspace.Subspace`.

`processOp` is the core dispatcher for operations after the `DIRECTORY_` prefix is removed. It handles creation of subspaces/layers, `CreateOrOpen`, `Create`, `CreatePrefix`, `Open`, `Change`, error-index setup, move operations, remove variants, list/exists, key pack/unpack/range/contains, subspace opening, directory/subspace logging, and prefix stripping.

## Control Flow

`processOp` wraps execution in a `defer`/`recover` block. Any panic stores `DIRECTORY_ERROR` at the current instruction index; for create/open/move operations it also appends `nil` to keep later object indexes aligned. Each case pops arguments from the stack in the instruction-defined order, invokes the directory/subspace API, and stores either a new object in the extension list or a stack result through `sm.store`.

Remove operations are intentionally wrapped in `t.Transact`, even when the incoming transactor is already database-like, so a failed non-`IF_EXISTS` removal does not accidentally commit a directory-version key written during the attempted removal.

## State and Persistence Behavior

The extension list is in-memory object state. Persistent state is FoundationDB directory metadata, directory contents, and explicit log outputs. `LOG_SUBSPACE` writes the current subspace bytes under a tuple-suffixed key. `LOG_DIRECTORY` writes path, layer, existence, and child list under a supplied root prefix. Create/move/remove operations mutate directory metadata transactionally through the supplied transactor.

## Dependencies and Integration Points

The file depends on the Go binding `fdb`, `directory`, `subspace`, and `tuple` packages. It is invoked from `StackMachine.processInst` in `stacktester.go` for `DIRECTORY_` operations. Its behavior must remain aligned with the Flow tester and other language binding directory tests, including placeholder insertion on errors.

## Risks

The object list stores `interface{}` values and relies on type assertions, so an invalid current index panics into `DIRECTORY_ERROR`. `tupleToPath` assumes every tuple element is a string. `CHANGE` maps a nil target to `errorIndex`, so wrong error-index setup can redirect subsequent operations. `LOG_SUBSPACE` appends tuple bytes to a mutable key slice, which is acceptable for immediate use but should not be reused as immutable input afterward.

## Test Signals

Signals come from generated binding stack tests that compare directory operation outputs across languages. Important cases include layer mismatch errors, manual-prefix behavior, moving across partitions, remove versus remove-if-exists, packing/unpacking keys, subspace containment, and directory logging after both successful and failed create/open operations.
