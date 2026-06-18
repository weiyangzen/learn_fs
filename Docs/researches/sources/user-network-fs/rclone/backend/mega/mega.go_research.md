# sources/user-network-fs/rclone/backend/mega/mega.go

## Purpose
`mega.go` implements rclone's MEGA backend using `github.com/t3rm1n4l/go-mega`. It adapts MEGA's encrypted, tree-oriented API to rclone's object storage interfaces, including login/session reuse, directory lookup/creation, listing, upload/download, delete, purge, server-side move and directory move, public links, duplicate directory merging, and quota reporting.

## Important APIs, Types, And Functions
`Options` contains user, password, 2FA code, hidden persisted session ID and master key, debug, hard delete, HTTPS transfer mode, and encoding. `Fs` stores the remote name/root, parsed options, features, shared `*mega.Mega`, pacer, cached root node, and mkdir mutex. `Object` stores the `Fs`, remote path, and pointer to a MEGA node.

Primary functions are `NewFs`, `findRoot`, `findNode`, `findDir`, `findObject`, `lookupDir`, `lookupParentDir`, `mkdir`, `mkdirParent`, `List`, `Put`, `PutUnchecked`, `Mkdir`, `Rmdir`, `Purge`, `CleanUp`, `move`, `Move`, `DirMove`, `PublicLink`, `MergeDirs`, `About`, `Object.Open`, `Object.Update`, `Object.Remove`, and `Object.ID`. `openObject` wraps chunked MEGA downloads as an `io.ReadCloser`.

## Control Flow
`NewFs` parses config, reveals the password, creates a pacer, advertises duplicate-file and empty-directory support, then retrieves or creates a cached `*mega.Mega` keyed by username. New sessions login with password and optional 2FA, persist `session_id` and base64 master key, and cache the connection. Existing sessions call `LoginWithKeys`. Root probing distinguishes existing directories, missing roots, and file roots.

Path resolution starts from the go-mega root node and uses encoded path parts with `FS.PathLookup`. `findRoot` caches the root node and optionally creates it. `mkdir` serializes directory creation, finds the deepest existing ancestor, then creates missing parts one by one.

Writes use `Put` to replace an existing object or `PutUnchecked` to create duplicates. `Object.Update` requires known length, creates parent directories, opens a MEGA upload, reads and uploads each chunk sequentially, finishes to obtain a node, and deletes the previous node if replacing. Reads call `NewDownload`, wrap it in `openObject`, skip chunks or offsets for range support, and finish the download in `Close` to surface MAC errors.

Moves create destination parents, find source parents, call `Move` if the parent changed, then `Rename` if the leaf changed, waiting briefly for MEGA events. Directory removal and purge share `purgeCheck`; optional hard deletion is controlled by config.

## State And Persistence Behavior
The backend persists session ID and master key back to rclone config after password login. In-memory state is dominated by the go-mega filesystem tree, shared through `megaCache` by username. `Fs._rootNode` caches the current backend root and is cleared after deleting or moving the root. `mkdirMu` serializes mkdir/rmdir/purge operations that mutate tree structure.

`Object` uses a MEGA node pointer rather than a plain ID because go-mega expects the whole tree in memory. This makes server-side moves simpler within a shared `*mega.Mega` but requires event waiting for the tree to settle after mutation.

## Dependencies And Integration Points
The backend integrates with rclone config, obscure, encoder, pacer, readers, fshttp, and optional interfaces (`Purger`, `Mover`, `PutUncheckeder`, `DirMover`, `DirCacheFlusher`, `PublicLinker`, `MergeDirser`, `Abouter`, `IDer`). All remote behavior is through go-mega. There is no supported content hash and modtime setting returns `fs.ErrorCantSetModTime`.

## Risks And Edge Cases
`megaCache` is keyed only by username, so remotes with different session settings for the same user intentionally share state. Upload and download chunks are sequential, which limits performance. `openObject.Close` must be called to finish and validate downloads. Range reads skip entire chunks then slice within a chunk, so off-by-one behavior depends on go-mega `ChunkLocation`. Update deletes the old node only after new upload finish; duplicate handling and delete failure can leave both versions. Directory cache flush is a stub.

## Test Signals
The integration test exercises broad backend conformance. Additional valuable coverage would target cached login/session persistence, root-as-file behavior, duplicate files, root deletion cache clearing, range reads, update replacement failure paths, hard-delete behavior, and server-side move/rename across cached remotes.
