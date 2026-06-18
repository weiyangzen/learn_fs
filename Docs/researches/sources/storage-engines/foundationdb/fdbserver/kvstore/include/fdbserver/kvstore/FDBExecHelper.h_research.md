# sources/storage-engines/foundationdb/fdbserver/kvstore/include/fdbserver/kvstore/FDBExecHelper.h

## Purpose
This header declares helper APIs for launching external FoundationDB-related commands and tracking storage versions by UID. It is an interface header; implementation lives elsewhere.

## Important APIs, Types, And Functions
`ExecCmdValueString` stores a command value string, parsed binary path, and binary arguments. Its API includes constructors, `setCmdValueString`, `getCmdValueString`, `getBinaryPath`, `getBinaryArgs`, and `dbgPrint`. `execHelper` asynchronously executes a parsed command for a snapshot UID, folder, role, and optional TLog spill folder. `setDataVersion`, `setDataDurableVersion`, and `printStorageVersionInfo` expose process-level version bookkeeping.

## Control Flow
Callers build or update an `ExecCmdValueString`, whose private `parseCmdValue()` populates `binaryPath` and `binaryArgs`. `execHelper` returns `Future<int>` so Flow actors can await process completion and status.

## State And Persistence Behavior
The command string and parsed argument refs live in `Standalone` arenas owned by the helper object. Version setter functions imply global state keyed by `UID`, but persistence semantics are not visible in this header.

## Dependencies And Integration Points
It depends on `FDBTypes`, `Arena`, and Flow futures. It likely integrates with snapshot, backup, restore, or spill workflows that shell out to helper binaries while preserving FoundationDB actor scheduling.

## Risks And Test Signals
Command parsing and argument lifetime are the main risks. Tests should verify whitespace/argument parsing, binary-path extraction, arena ownership after `setCmdValueString`, async exit-code propagation from `execHelper`, and version bookkeeping for multiple UIDs.
