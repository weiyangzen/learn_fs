# sources/user-network-fs/rclone/backend/mailru/mailru.go

## Purpose
`mailru.go` implements rclone's Mail.ru Cloud backend. It registers the `mailru` remote, authenticates through Mail.ru OAuth password credentials or stored tokens, translates rclone `fs.Fs` and `fs.Object` operations into Mail.ru JSON and binary API calls, and supplies Mail.ru-specific hash handling through `mrhash`. The file covers directory listing, object metadata, uploads, downloads, server-side copy and move, directory move, public links, cleanup, quota, deletion, and optional upload acceleration by "put by hash".

## Important APIs, Types, And Functions
Important exported surfaces are `NewFs`, `Fs`, `Object`, `Mkdir`, `Rmdir`, `Purge`, `List`, `NewObject`, `Put`, `Copy`, `Move`, `DirMove`, `PublicLink`, `CleanUp`, `About`, `Object.Update`, `Object.Open`, `Object.Hash`, and `Object.SetModTime`. The backend registers a custom `MrHashType` with rclone's hash registry and advertises optional features for case-insensitive names, empty directories, and server-side cross-config operations.

`Options` contains credentials, user agent override, hash checking, speedup settings, troubleshooting quirks, and encoding policy. `quirks` enables experimental binary listing, atomic mkdir semantics, and acceptance of unknown directory kinds. `serverPool` manages temporary download server URLs with lock counts and expirations. `treeState` and `treeRevision` parse Mail.ru's binary folder-list format.

Core helpers include `authorize`, `reAuthorize`, `accessToken`, `metaServer`, `uploadShard`, `readItemMetaData`, `itemToDirEntry`, `isDir`, `listM1`, `listBin`, `CreateDir`, `mkDirs`, `mkParentDirs`, `delete`, `moveItemBin`, `eligibleForSpeedup`, `parseSpeedupPatterns`, `putByHash`, `makeTempFile`, `upload`, `addFileMetaData`, `getTransferRange`, and the `endHandler` read closer.

## Control Flow
Construction parses config, reveals the password, trims the root, parses speedup patterns and quirks, builds a pacer and HTTP/rest clients, authorizes, initializes the download server pool, and probes the root unless a trailing slash declares it a directory. If the root is a file, `NewFs` returns an Fs pointing to the parent with `fs.ErrorIsFile`.

Listing chooses JSON `m1` folder listing by default, or binary listing when the `binlist` quirk is enabled. JSON listing posts `home` to `/api/m1/folder`; binary listing gets a meta server, sends an encoded operation, reads status/revision/space/fingerprint data, and iterates parse records through `treeState.NextRecord`. API items become rclone directories or objects after root-relative path normalization and Mail.ru hash decoding.

Writes call `Object.Update`. The method rejects unknown-size streams, creates parents, then tries several upload acceleration routes: instant source `MrHashType`, local-source hash, in-memory hashing, or a temporary local spool file. If put-by-hash fails or is ineligible, it uploads data to a dispatch-selected shard and verifies the returned Mail.ru hash. Finally it commits metadata through the binary add-file operation. Small files of at most `mrhash.Size` can skip upload and store content through the hash buffer.

Reads select a download server from `serverPool`, issue a GET with optional range headers, and wrap the body in `endHandler`. Full downloads are hashed during streaming and compared with the stored Mail.ru hash when EOF is reached; partial responses skip checksum validation. Copy and move create parents, call Mail.ru copy or binary rename endpoints, and copy fixes destination modtime by rewriting metadata if needed.

## State And Persistence Behavior
Persistent user-facing state is remote Mail.ru content plus OAuth tokens saved through `oauthutil.PutToken`. Runtime state includes `Fs.source`, cached meta and shard URLs with expiry times, `serverPool` download server locks, parsed speedup globs, and quirk flags. `Object` caches remote path, metadata freshness, size, modtime, and binary Mail.ru hash. The backend does not maintain a local directory cache; metadata is refreshed on demand.

Concurrency is protected by `authMu`, `metaMu`, `shardMu`, and `serverPool.mu`. Reauthorization is deliberately one-shot after a 403 when a password is configured. The download server pool increments lock counts on dispatch and decrements them when `endHandler` reaches EOF or closes. Upload spool files are created under rclone's temporary local Fs and purged with a deferred cleanup.

## Dependencies And Integration Points
The backend integrates with rclone's `fs`, config, obscure, OAuth, pacer, rest, object, operations, readers, hash, and encoder packages. It depends on `backend/mailru/api` for endpoints, response types, binary writer/reader constants, and OAuth constants, and on `backend/mailru/mrhash` for Mail.ru checksums. Server-side copy/move interacts with rclone's optional interfaces and allows cross-config operations only when usernames match.

## Risks And Edge Cases
The password OAuth flow and query-parameter token placement are service-specific and fragile. `reAuthorize` uses a background context because it is invoked from retry logic, so cancellation does not propagate. Binary listing is explicitly experimental and only emits level-one entries. `Object.Hash` returns the cached hash without forcing metadata, so callers must ensure metadata was loaded. Directory root move guards compare path lengths against roots and should be tested around empty roots. Speedup can consume memory or disk and depends on correct source hash reporting; the spool path validates SHA1 but still adds operational complexity. Partial downloads rely on server range behavior and fall back to discarding leading bytes if the server sends a full response.

## Test Signals
Important test signals include configured integration tests through `mailru_test.go`, upload/download hash mismatch behavior with `check_hash` on and off, speedup eligibility for patterns, max memory/disk and partial transfers, small-file commit without upload, OAuth token refresh after 403, binary and JSON list parity, mkdir quirks, copy/move/DirMove across same and different accounts, range reads, and server-pool lock release on EOF and early close.
