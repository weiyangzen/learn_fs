# sources/sync-backup/kopia/repo/content/content_manager_lock_free.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/content_manager_lock_free.go_research.md`.

Purpose: contains helper paths intentionally run outside or around the main write-manager lock: compression/encryption, pack preparation, read payload extraction, pack upload, IV derivation, and hashing.

Important APIs: `maybeCompressAndEncryptDataForPacking` handles optional compression, rejects compression for v1 indexes, disables metadata compression before index v2, and encrypts using an IV derived from the content ID. `getContentDataReadLocked` reads from a pending pack buffer or cache-backed blob section and calls `decryptContentAndVerify`. `preparePackDataContent` builds a per-pack `index.Builder`, adds padding, appends local recovery index data, and marks a pack finalized. `writePackFileNotLocked` uploads a pack blob and records metrics. `hashData` computes repository content hashes.

Control flow, State and persistence: pack data is prepared exactly once via `pp.finalized`. Pending pack records can include entries moved from older packs, deleted markers, or new content. If no live content remains after a preamble, the preamble buffer is reset while index entries are still returned. Padding uses random bytes to align to `paddingUnit`, then local recovery metadata is appended.

Dependencies: compression registry, format encryptor/hash provider, gather buffers, content and blob caches, OpenTelemetry tracing, metrics, and pack recovery code.

Risks: compression mutates the effective payload used for encryption, so cache keys include format metadata. Pending pack section reads must be protected while pack buffers can still grow. V1 original lengths are inferred from packed length and encryptor overhead. Tests cover failed-write aliasing, compression behavior, cache-by-format, and read/write aliasing.
