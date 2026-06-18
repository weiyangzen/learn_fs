# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/BackupContainerFileSystem.h

Purpose: filesystem-like implementation base for `IBackupContainer`, defining common backup path schemes and higher-level container behavior atop storage-specific file operations.

Important APIs and types: subclasses provide `listFiles`, `readFile`, `writeFile`, `writeEntireFile`, `deleteFile`, create/exists, and refcounting. This base finalizes log/range/keyspace snapshot writing, partition list writing, log/range/snapshot listing, file-list dumping, describe, expiration, snapshot key-range inspection, restore-set computation, encryption metadata, and encryption setup.

Control flow: path conventions group snapshots under `snapshots`, key range files under `kvranges`, partitioned logs under `plogs`, old logs under `logs`, and old range files under `ranges` for backward compatibility. `VersionProperty` helper stores boundary versions in `properties/*` to avoid full filesystem scans.

State and persistence: persists backup files, snapshot manifests, partition lists, version boundary properties (`logBeginVersion`, `logEndVersion`, `expiredEndVersion`, `unreliableEndVersion`, `logType`), and encryption metadata. `encryptionSetupFuture` tracks async key setup.

Dependencies and integration: inherits `IBackupContainer`, uses `fmt`, FDB types, Trace, and concrete local/blob filesystem-like backends.

Risks: path format is a restore compatibility surface across FDB versions. Expiration and deep-scan logic must coordinate cached version properties with actual file listings. Encryption key setup must complete before reads/writes that need it.

Test signals: backup container filesystem tests for old/new path parsing, list/describe, restore-set generation, expiration safety, and encryption metadata.
