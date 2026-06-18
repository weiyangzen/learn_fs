# sources/distributed-fs/tahoe-lafs/src/allmydata/storage/server.py

## Purpose
Implements the local filesystem storage server and its Foolscap remote adapter. `StorageServer` manages immutable bucket allocation/reading, mutable slot read/test/write operations, lease lifecycle, corruption advisories, storage statistics, reserved-space accounting, and crawler services.

## Important APIs, Types, And Functions
`StorageServer` provides `get_version()`, `allocate_buckets()`, `add_lease()`, `renew_lease()`, `get_buckets()`, `get_shares()`, `slot_testv_and_readv_and_writev()`, `slot_readv()`, `enumerate_mutable_shares()`, `advise_corrupt_share()`, and share length helpers. Internal helpers collect mutable shares, evaluate test/read/write vectors, allocate slot shares, make leases, and add or renew leases. `FoolscapStorageServer` exposes the same behavior as `remote_*` methods and wraps `BucketWriter`/`BucketReader` objects for Foolscap. `render_corruption_report()` and `get_corruption_report_path()` create advisory files.

## Control Flow
Startup creates `shares`, `incoming`, and corruption-advisory directories, removes incomplete uploads, registers stats, and starts bucket-counting and lease-checking crawlers. Immutable allocation records existing shares, renews leases if requested, subtracts already allocated in-progress space, creates `BucketWriter` instances in `incoming`, and later receives close callbacks. Mutable write flow validates write enablers for all existing shares, evaluates test vectors, reads requested old data before writes, applies writes and deletions only if tests pass, and renews leases on remaining shares.

## State And Persistence
Persistent state lives under `storage/shares/<prefix>/<storage-index>/<sharenum>`, with incomplete immutable uploads under `shares/incoming` and corruption reports under `corruption-advisories`. Runtime state includes in-progress `_bucket_writers`, latency samples capped to 1000 entries per category, stats producer registration, crawler state/history files, and close handlers. Lease data persists inside share files.

## Dependencies And Integration Points
The server integrates with `ShareFile`, `BucketWriter`, `BucketReader`, `MutableShareFile`, lease and crawler modules, Tahoe RI interfaces, Twisted `MultiService`, Foolscap `Referenceable`, filesystem utilities, storage-index path helpers, and client-side `storage_client` protocol adapters.

## Risks And Test Signals
Risks include space accounting races, incomplete-upload cleanup, mutable test/write atomicity, zero-length mutable deletion, bad write-enabler migration diagnostics, corruption-report disk checks, and differences between readonly/discard modes and normal storage. Tests should cover immutable allocation under reserved space, connection-loss aborts, lease add/renew behavior on mixed mutable/immutable shares, mutable CAS success/failure, read-before-write semantics, bucket directory cleanup, advisory creation, stats fields, and Foolscap wrapper parity.
