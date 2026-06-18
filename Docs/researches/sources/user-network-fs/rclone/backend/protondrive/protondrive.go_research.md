# sources/user-network-fs/rclone/backend/protondrive/protondrive.go

## Purpose
Proton Drive backend: authenticates with Proton credentials or cached reusable tokens; wraps Proton-API-Bridge; maps encrypted Proton links into rclone files/directories; supports list, upload, download, move, delete, quota, logout, hash, MIME, and dir-cache behavior.

## Important APIs, Types, And Functions
Important surface: Options, Fs, Object, protonLogger, get/set/clear config map helpers, app-version helpers, newProtonDrive, NewFs, List, FindLeaf, CreateDir, Put, Mkdir, Rmdir, Purge, About, Move, DirMove, Disconnect, and object Open/Update/Remove/Hash methods.

## Control Flow
NewFs reveals obscured secrets, configures rclone HTTP transport/logging, tries reusable login then username/password/TOTP fallback, creates a dircache rooted at the Proton main share, and returns fs.ErrorIsFile for file roots. Listing decrypts directory data through the bridge; upload rejects unknown sizes and calls UploadFileByReader; download calls DownloadFileByID and wraps range limits.

## State And Persistence
remote links, revisions, trash, encrypted attrs, reusable token config keys, package-level auth callback state, dircache, object metadata, API bridge cache.

## Dependencies And Integration Points
Proton-API-Bridge, go-proton-api, semver, totp, rclone fs/config/obscure/fshttp/dircache/encoder/pacer/readers/hash.

## Risks And Test Signals
Risks and useful test signals: global auth callback state for simultaneous remotes, stale cache with external clients, no multi-threaded downloads, 429/503 delegated to SDK, root purge prevention, destination conflicts.
