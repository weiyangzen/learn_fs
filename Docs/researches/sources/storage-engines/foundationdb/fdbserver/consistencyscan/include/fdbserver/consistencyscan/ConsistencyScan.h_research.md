# sources/storage-engines/foundationdb/fdbserver/consistencyscan/include/fdbserver/consistencyscan/ConsistencyScan.h

## Purpose
This public header exposes the consistency scan role entry point and the legacy consistency-check workload helpers implemented in `ConsistencyScan.cpp`.

## Important APIs
`consistencyScan(ConsistencyScanInterface, Reference<AsyncVar<ServerDBInfo> const>)` starts the server role. `getKeyServers` asks commit proxies for shard-to-storage mappings over a key range. `getKeyLocations` reads key-location metadata from storage servers and verifies replica agreement. `checkDataConsistency` performs the main workload-level shard data, metric, team-size, TSS, split, and sampling checks. The header also declares `Future<Version> getVersion(Database cx)`.

## Control flow and state
The header declares APIs only. Callers provide the database or role interface, promises for async results, consistency-check mode flags, client distribution parameters, rate settings, and mutable output pointers such as `success` and `bytesReadInPreviousRound`. Runtime state is kept in the implementation and in caller-owned arguments.

## Dependencies and integration points
The header includes `fdbclient/ConsistencyScanInterface.h` and `flow/flow.h`, relying on transitive availability of FoundationDB database, key range, storage server, and configuration types. It is the exported include path from the `fdbserver_consistencyscan` CMake target and is consumed by server role wiring and consistency workload code.

## Risks and test signals
The declaration `getVersion(Database cx)` does not match the implementation name `getStorageServerReadVersion(Database cx)` in the corresponding source file. If no compatibility wrapper exists elsewhere, any caller using `getVersion` will fail to link; if nobody uses it, the mismatch can remain latent. The large `checkDataConsistency` signature is brittle because many booleans and counters are positional. Link tests and workload builds are the primary signals for API drift, while simulation consistency-check workloads validate behavior.
