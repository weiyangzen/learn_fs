# sources/sync-backup/kopia/repo/content/content_index_recovery.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/content_index_recovery.go_research.md`.

Purpose: implements pack-local index recovery metadata. `WriteManager.RecoverIndexFromPackBlob` reads the encrypted local index embedded at the end of a pack blob, opens it through `index.Open`, returns recovered `Info` entries, and optionally commits them into the unflushed `packIndexBuilder`.

Important APIs and types: `packContentPostamble` records the local-index IV, offset, and encrypted length. `toBytes`, `findPostamble`, and `decodePostamble` encode and validate a CRC32-protected postamble. `SharedManager.buildLocalIndex` and `appendPackFileIndexRecoveryData` build a normal index, encrypt it, append it to pack data, then append the postamble.

Control flow, State and persistence: pack writing calls `appendPackFileIndexRecoveryData` from `preparePackDataContent` before upload. Recovery locates the postamble, decrypts the referenced local index, iterates every content record, and adds those records to the session index only when `commit` is true. The CRC is only corruption detection for locating metadata; authenticity still comes from decrypting the index payload.

Dependencies and integration: depends on `gather`, repository `format.Encryptor`, `blob.ID`, and the content `index` package. It integrates with pack writes in `content_manager_lock_free.go` and with recovery tests that delete committed index blobs.

Risks: postamble offsets and lengths are stored as `uint32`, so very large pack/index sizes rely on repository limits. `findPostamble` deliberately treats a valid CRC as a recovery hint, not a trust boundary. Committing recovered entries updates only local unflushed state until `Flush`.

Test signals: covered by `content_index_recovery_test.go`, which removes index blobs, verifies contents disappear, recovers without commit, then recovers with commit and flushes durable replacement indexes.
