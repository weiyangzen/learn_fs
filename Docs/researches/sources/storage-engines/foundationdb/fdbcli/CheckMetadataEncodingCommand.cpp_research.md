# sources/storage-engines/foundationdb/fdbcli/CheckMetadataEncodingCommand.cpp

Purpose: Implements an audit helper that scans shard metadata encoding state and reports whether key-server/server-key metadata is old format, new format, mixed, or safe for rollback.

Important APIs/types/functions: `checkMetadataEncodingCommandActor(Database, tokens)` scans `keyServersPrefix..keyServersEnd`, `serverKeysPrefix..strinc(serverKeysPrefix)`, and `dataMoveKeys`. It uses `BinaryReader` with `IncludeVersion`, `rd.protocolVersion().hasShardEncodeLocationMetaData()`, constants `serverKeysTrue`, `serverKeysFalse`, `serverKeysTrueEmptyRange`, and transaction options `READ_SYSTEM_KEYS`, `READ_LOCK_AWARE`, and `PRIORITY_SYSTEM_IMMEDIATE`.

Control flow: The actor initializes counters, scans keyServers in 1000-row pages, classifies empty values and old protocol encodings as old, and newer shard-location metadata encodings as new. It separately scans serverKeys and treats legacy constant values as old, anything else as UID-encoded new. It then reads up to `CLIENT_KNOBS->TOO_MANY` data-move rows and prints counts plus a derived migration status. Each scan loop creates/reuses transactions and uses `onError` for retry, except the data-move section performs one retry path if an error was captured.

State and persistence behavior: Read-only against system metadata. No local state or cluster mutation. It reads live metadata, so output is a snapshot-like diagnostic and can change while migration is running.

Dependencies and integration points: Used by audit-storage command paths for metadata encoding validation. Depends on system data layout, binary protocol-version tagging, and key-range constants from fdbclient.

Risks: Classifying unknown non-legacy serverKeys values as new is intentionally broad. The data-move count uses a single `TOO_MANY` bounded read; if invariants are violated and more rows exist than expected, this command does not page the range. It also assumes metadata values are decodable.

Test signals: Tests should exercise all-old, all-new, mixed, rollback-complete with zero data moves, and data-move-present states. Fault injection around transaction retries and malformed metadata would protect the diagnostic path.
