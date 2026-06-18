# sources/storage-engines/foundationdb/fdbcli/DebugCommands.cpp

Purpose: Provides hidden debugging commands for locating storage replicas, reading all replica values for a key, and comparing all replicas over a key range for inconsistency diagnostics.

Important APIs/types/functions: `toHex`, `getVersion`, `getKeyServers`, `getLocationCommandActor`, `getallCommandActor`, `printStorageServerMachineInfo`, `printAllStorageServerMachineInfo`, `checkResults`, `doCheckAll`, and `checkallCommandActor`. It uses `CommitProxyInterface::getKeyServersLocations`, `GetKeyServerLocationsRequest`, `StorageServerInterface::getValue`, `StorageServerInterface::getKeyValues`, `getKeyLocation_internal`, `GetKeyValuesRequest`, and `CLIENT_KNOBS->KRM_GET_RANGE_LIMIT*`.

Control flow: `getlocation` asks commit proxies for shard-to-storage-server mappings over a key or range and prints server addresses. `getall` resolves a key at a supplied version and sends parallel `GetValueRequest`s to every replica location. `checkall` parses begin/end, optional DCID and `all`, then `doCheckAll` repeatedly resolves shard locations, queries all replica storage servers at the same read version, determines a comparison window from returned keys and `more` flags, and calls `checkResults` to log unique-key or mismatched-value inconsistencies. A recursive sub-check avoids getting stuck when paginated replies end at the current begin key.

State and persistence behavior: Read-only diagnostics. It bypasses ordinary transactional range reads and contacts commit proxies/storage servers directly, using retry delays and transaction `onError` only for read-version/backoff support.

Dependencies and integration points: Depends on NativeAPI internals, commit proxy and storage server interfaces, Flow `race`, `waitForAll`, `CoroUtils`, and hidden `CommandFactory` registrations for `getlocation`, `getall`, and `checkall`.

Risks: Intended for small ranges; `checkall` can be expensive and noisy. Direct server RPCs expose failures differently from transaction reads. DCID filtering only excludes servers with a different present dcid; if cluster/server dcid is absent, the filter is ignored. Comparison logic is subtle around pagination and clear operations.

Test signals: Unit tests should target `checkResults` mismatch cases and pagination invariants. Integration tests should cover location lookup, replica value reads, DCID filtering, recursive progress when `begin == claimEndKey`, stop-on-first vs `all`, and server RPC error retry.
