# sources/sync-backup/syncthing/cmd/stdiscosrv/database.go

Purpose: provides the discovery server's in-memory database with periodic protobuf persistence, expiry, statistics, and optional blob-store backup/restore.

Important APIs/types/functions: `clock`, `database`, `inMemoryStore`, `newInMemoryStore`, `put`, `merge`, `get`, `Serve`, `expireAndCalculateStatistics`, `write`, `read`, `merge`, `expire`, `Cmp`, and `Equal`.

Control flow: construction reads `records.db`, falls back to downloading the latest blob object if configured and the local file is missing, logs record count, then expires records and calculates metrics. `Serve` periodically runs statistics and `write`, and writes one final time on shutdown. `get` expires returned addresses lazily. `merge` combines new and old sorted address lists using latest expiry and latest seen timestamp. `write` serializes length-prefixed protobuf `ReplicationRecord` entries to a temp file, renames atomically, and uploads to blob storage when configured.

State and persistence: live state is an `xsync.MapOf[protocol.DeviceID,*DatabaseRecord]`. Durable state is `records.db` in the configured database directory, with records older than one week omitted. Optional S3/blob upload uses a hostname-derived object key.

Dependencies/integration: uses generated `discosrv` protobufs, Syncthing device IDs, `protoutil`, `blob.Store`, Prometheus database metrics, and the API/AMQP layers.

Risks and test signals: `merge` assumes both address slices are sorted; API and read paths sort before merge, but direct callers must preserve that contract. The insertion path allocates when `b` has new earlier addresses; benchmark tracks equal-list allocations. Old records are deleted by statistics/write filtering. Tests cover put/get, expiry filtering, merge symmetry, and benchmark allocation behavior.
