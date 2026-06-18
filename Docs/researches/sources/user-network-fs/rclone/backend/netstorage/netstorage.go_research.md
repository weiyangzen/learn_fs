# sources/user-network-fs/rclone/backend/netstorage/netstorage.go

## Purpose
`netstorage.go` implements rclone's Akamai NetStorage backend. It maps rclone object operations to NetStorage action-header HTTP requests signed with Akamai ACS auth headers. It supports listing, recursive listing with resume, uploads with SHA256 trailer signing, downloads with range options, MD5 hashes, modtime setting, empty directories, quick-delete purge, directory creation/removal, symlink adaptation through `.rclonelink`, and backend commands for `du` and `symlink`.

## Important APIs, Types, And Functions
`Options` contains endpoint host/path, account, secret, and protocol. `Fs` stores endpoint URL, rest client, pacer, root type, implicit directory map, and stat cache. `Object` stores remote path, file type, size, mtime, MD5, full URL, and symlink target. XML response types are `Stat`, `File`, `List`, `ListResume`, `Du`, and `DuInfo`.

Important methods include `NewFs`, `Command`, `NewObject`, `initFs`, `url`, `getFileName`, `List`, `ListR`, `Put`, `PutStream`, `implicitCheck`, `Purge`, `Mkdir`, `Rmdir`, `Object.Update`, `Object.Open`, `Object.Remove`, `SetModTime`, `newObjectWithInfo`, `getAuth`, `callBackend`, `netStorageStatRequest`, `netStorageDirRequest`, `netStorageListRequest`, `netStorageUploadRequest`, `netStorageDownloadRequest`, `netStorageDuRequest`, `netStorageSymlinkRequest`, and signing helpers.

## Control Flow
`NewFs` parses config, prefixes protocol onto the host/path, reveals the secret, joins the root into the endpoint URL, installs `getAuth` as the rest signer, fills features, and stats the root. If the root is a file or symlink, the endpoint and root are adjusted to the parent and `fs.ErrorIsFile` is returned.

Every backend call uses an `X-Akamai-ACS-Action` action string. `getAuth` builds `X-Akamai-ACS-Auth-Data` with account, timestamp, and random request ID, then signs data, request URI, and action with HMAC-SHA256. `callBackend` chooses raw or XML REST calls, applies pacer retry policy for selected HTTP status codes, and maps 404 to rclone not-found errors.

Listing uses `dir` for direct children and `list` for recursion. Recursive listing follows `resume.start`, rebuilds URLs from the endpoint, trims NetStorage CP-code prefixes, and converts symlinks into `.rclonelink` objects for local backend compatibility. Upload first calls `implicitCheck` to create all parent directories, then uses chunked upload with `sha256=atend` and `mtime=atend`, writing final action/auth trailers when the reader reaches EOF. Downloads issue `action=download` and delegate range normalization to `fs.FixRangeOption`.

## State And Persistence Behavior
Remote state lives in NetStorage. Local mutable state includes `dirscreated`, which avoids repeated implicit mkdir calls, and `statcache`, which caches successful stat responses by trimmed URL. Both maps are mutex-protected. Mutating operations invalidate the stat cache for affected URLs and remove dirscreated entries on rmdir.

The backend does not maintain a full directory cache. Empty directory support is remote-backed through mkdir/rmdir. Symlinks are represented as synthetic `.rclonelink` objects on list/stat/download/upload/delete.

## Dependencies And Integration Points
The file integrates with rclone `fs`, config, obscure, fshttp, rest, pacer, list helper, hash, and optional `Purger`, `PutStreamer`, and `ListRer` interfaces. It depends on XML response contracts from Akamai NetStorage and the ACS authentication scheme.

## Risks And Edge Cases
`getAuth` assumes the action header exists and indexes it directly; callers must always set it. `generateRequestID` creates a new time-seeded random source for each call, which is simple but not collision-proof under extreme concurrency. `implicitCheck` explicitly does not detect conflicts with existing files or dirs and can create duplicates per its comment. Stat cache invalidation is URL-local and may miss parent list effects. Quick-delete purge is asynchronous and returns `fs.ErrorCantPurge` on failure to trigger fallback. Upload failure attempts to remove the object, which can mask partial remote behavior.

## Test Signals
The integration test covers broad behavior against a configured remote. Additional focused tests should cover ACS signing strings, base64 filename fallback, stat cache invalidation, `.rclonelink` conversions, implicit directory creation, list resume handling, upload trailer signing, and command outputs for `du` and `symlink`.
