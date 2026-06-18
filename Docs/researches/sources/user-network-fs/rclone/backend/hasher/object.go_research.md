
# sources/user-network-fs/rclone/backend/hasher/object.go

## Purpose
This file implements the object-level behavior of rclone's `hasher` overlay backend. It wraps an underlying `fs.Object` so hashes can be passed through, cached in the hasher key/value database, calculated while reading or uploading, and pruned when object identity changes.

## Important APIs, Types, And Control Flow
`Object.Hash` is the central API. It first asks the wrapped object for pass-through hashes when the base remote supports them, then checks whether the requested type is supported by the hasher overlay, then consults `getHash`/`getRawHash` in the KV database using a fingerprint, and finally falls back to slow base hashes or automatic download hashing for small objects. `Open` detects partial reads from `SeekOption` and `RangeOption`; only full-object reads are wrapped with `hashingReader` so a complete stream updates cached checksums. `Put` wraps upload input with `newHashingReader` when source hashes are incomplete or slow, otherwise copies available source hashes into the cache after the base `Put`. `Update`, `Remove`, and `SetModTime` prune stale cache entries before delegating to the wrapped object.

## State And Persistence
Persistent state is the hasher database entry keyed by `path.Join(f.Fs.Root(), remote)`, a fingerprint, and hash names. `putRawHashes` writes through `kvPut` with `MaxAge`; `getRawHash` reads through `kvGet` and enforces age. The fingerprint is derived from size, optional modtime, and optional fast hash from the underlying remote, deliberately avoiding `fs.Fingerprint` to prevent hasher-produced hash recursion.

## Dependencies And Integration Points
The file depends on rclone `fs`, `hash`, and `operations.HashSums`, the backend's `kvGet`/`kvPut`/`pruneHash` helpers, and wrapped object interfaces. It integrates with `fs.OpenOption` range semantics, `hash.MultiHasher`, and rclone upload/download flows.

## Risks And Test Signals
Partial reads intentionally do not refresh hashes; incorrect range detection would poison cache data. Failed `fingerprint` returns suppress caching and may hide backend hash/modtime errors. `Put` may rehash streams only when `newHashingReader` succeeds; source-provided hashes are trusted if rehashing is not needed. `SetModTime` only prunes when the timestamp differs from the current modtime. Good tests exercise cache hits/misses, `MaxAge <= 0`, pass-through blank hashes, slow hash storage, partial `Open`, upload with and without complete source hashes, and pruning on update/remove/touch.
