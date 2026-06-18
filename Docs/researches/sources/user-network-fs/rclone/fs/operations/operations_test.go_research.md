# Research: sources/user-network-fs/rclone/fs/operations/operations_test.go

## sources/user-network-fs/rclone/fs/operations/operations_test.go

Purpose: broad integration and unit coverage for `fs/operations`, usually through `fstest.Run` against local or configured remotes. It validates public operation behavior rather than implementing production APIs. Important signals include listing variants, `HashLister`, `HashSumStream`, delete/max-delete limits, `Cat`, `Purge`, `Rmdirs`, `CopyURL`, `MoveFile`, overlap checks, `ListFormat`, `DirMove`, `Rcat`, directory metadata/modtime, `DirsEqual`, and `RemoveExisting`.

Control flow is table-driven where possible and otherwise builds remote/local fixtures, writes objects, invokes operations, then checks object and directory listings with precision-aware assertions. State is mostly test fixture state plus context-local config mutations via `fs.AddConfig`, filter replacement, accounting resets, and backend feature toggles. Integration points cover `fstest`, `filter`, `accounting`, `fshttp`, `hash`, `pacer`, and backend feature interfaces. Risks caught include global config non-concurrency, backend capability skips, eventual listing consistency, delete safeguards, case-insensitive moves, metadata support, and temporary backup cleanup. Test signal is very strong for operations behavior across real backends.
