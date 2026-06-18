# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/filenode.py

## Purpose
Provides user-facing immutable file node wrappers. `CiphertextFileNode` reads/checks encrypted CHK content by verifycap; `ImmutableFileNode` wraps it with the read key to expose plaintext reads and immutable filesystem node APIs.

## Important APIs, Types, And Functions
`CiphertextFileNode` lazily creates a `DownloadStatus` and `DownloadNode` on first read/segment access. It exposes `read`, `get_segment`, `get_segment_size`, verifycap/size/storage-index accessors, `check`, and `check_and_repair`.

`DecryptingConsumer` implements `IConsumer` and `IDownloadStatusHandlingConsumer`. It wraps a downstream consumer, constructs an AES CTR decryptor positioned to the requested offset, passes producer registration through, decrypts each ciphertext chunk in `write()`, and records decrypt timing.

`ImmutableFileNode` implements `IImmutableFileNode`. It stores the CHK read cap and read key, delegates reads through `DecryptingConsumer`, exposes URI/cap/readcap/verifycap/repair-cap/size methods, immutable/read-only predicates, check/repair delegation, and `download_best_version`/`download_to_data`.

## Control Flow
Reading plaintext creates a `DecryptingConsumer`, calls ciphertext node `read()`, and maps the callback back to the original consumer. The ciphertext node creates shared download status/node if needed, adds download status to history, and delegates range reads or segment fetches.

Checking constructs a `Checker` over connected servers and starts it. `check_and_repair()` runs the checker, returns unchanged results if healthy, or starts `Repairer` and merges original check results with upload repair results in `_gather_repair_results()`.

Repair result gathering builds a new sharemap by unioning pre-existing good shares and newly uploaded shares, recomputes good hosts, health, recoverability, servers-of-happiness, corrupt/incompatible counts, and fills `CheckAndRepairResults`.

## State And Persistence
`CiphertextFileNode` keeps one lazily initialized `DownloadNode` and `DownloadStatus`, so multiple reads share learned UEB/hash/share state. `ImmutableFileNode` stores immutable cap and read key only. Repair can cause remote writes through `Repairer`; check can renew leases when requested through `Checker`.

## Dependencies And Integration Points
Depends on CHK URI classes, AES crypto, Twisted Deferreds, consumer utilities, `Checker`, `Repairer`, `DownloadNode`, `DownloadStatus`, `CheckResults`, `CheckAndRepairResults`, `DictOfSets`, and `servers_of_happiness`. Client, directory, web, and system layers use `IImmutableFileNode`.

## Risks And Edge Cases
`DecryptingConsumer` manually advances AES CTR for unaligned offsets; offset arithmetic must match encryption. `__ne__` appears to return `self.u.__eq__(other.u)` for another immutable node, which is logically inverted relative to `__eq__`. Repair health uses `len(sm) >= total_shares` for healthy, mirroring checker semantics, and may not indicate ideal distribution beyond happiness count. Download status/history are only created on demand.

## Test Signals
`src/allmydata/test/test_filenode.py` covers immutable equality/interfaces. `test_download.py`, `test_system.py`, `test_client.py`, and directory/web tests exercise reads, downloads, and node integration. Repair behavior is covered in `test_repairer.py`.
