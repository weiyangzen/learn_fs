# sources/sync-backup/kopia/repo/content/content_manager.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/content_manager.go_research.md`.

Purpose: central write/read content manager for Kopia's content-addressable storage. It hashes content IDs, compresses and encrypts payloads, batches content into pack blobs, tracks pending and committed indexes, handles deletion markers, and flushes session state to durable index blobs.

Important APIs and types: `WriteManager` owns mutable session state: pending/writing/failed packs, `packIndexBuilder`, flush barriers, session identity, upload accounting, and a shared committed read manager. `pendingPackInfo` stores pack data and `Info` records before upload. Public APIs include `WriteContent`, `GetContent`, `ContentInfo`, `DeleteContent`, `UndeleteContent`, `RewriteContent`, `Flush`, `DisableIndexFlush`, `EnableIndexFlush`, `Revision`, and construction helpers.

Control flow: `WriteContent` validates the prefix, hashes input, checks overlay and committed indexes for dedupe, then calls `addToPackUnlocked`. That path may auto-flush old indexes, compress/encrypt outside the main lock, retries failed packs, appends bytes to a pending pack, and uploads a full pack without holding the lock. `Flush` blocks new pack uploads, retries failed writes, waits for in-flight uploads, writes all pending packs, builds index shards, writes index blobs, commits the session marker, and adds new indexes to committed contents. Reads take an `RLock` so info lookup and payload fetch see a consistent pending-pack state.

State and persistence behavior: pending pack data is memory-resident until pack upload; uploaded pack entries live in `packIndexBuilder` until index flush; committed index blobs become visible after session commit. Deletions are represented as newer `Info` records with `Deleted=true` and monotonic timestamps. Failed pack writes remain in `failedPacks` for retry.

Dependencies and integration: depends on `blob.Storage`, `format.Provider`, `compression`, `gather`, `index`, `indexblob`, cache/log/session helpers, metrics, and `SharedManager` for committed reads and decryption.

Risks: lock ordering around `mu`, `indexesLock`, and session commits is critical. Timestamp ordering determines delete/recreate conflict resolution. Compression support is tied to index version. Failed writes must never lose `currentPackData`. Tests heavily cover these behaviors in `content_manager_test.go`.
