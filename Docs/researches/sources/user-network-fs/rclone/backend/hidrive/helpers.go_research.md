
# sources/user-network-fs/rclone/backend/hidrive/helpers.go

## Purpose
This file contains the HiDrive backend's operational helper layer: retry decisions, path resolution, paginated directory iteration, metadata fetch, copy/move, directory creation/deletion, file create/overwrite/patch/truncate, parallel chunked uploads, scope creation, and repeatable reader utilities.

## Important APIs, Types, And Control Flow
`shouldRetry` handles context cancellation, OAuth token expiry on 401 with `Www-Authenticate`, generic retryable errors, and retryable HTTP codes. `resolvePath` joins root prefix, backend root, and encoded path. `iterateOverDirectory` and `paginateDirectoryAccess` issue `/dir` requests with `limit=offset,count` windows. `createDirectories` recursively creates parents after `fs.ErrorDirNotFound`. File helpers distinguish `createFile` POST, `overwriteFile` PUT, `patchFile` PATCH at offsets, and `resizeFile` truncate/extend. `updateFileChunked` reads fixed chunks, uses an errgroup plus semaphore for parallel `patchFile` calls, records successful byte ranges, and returns the first continuous uploaded size.

## State And Persistence
Stateful effects are API mutations: directories and files are created, moved, copied, deleted, patched, resized, and timestamped. Chunked uploads are explicitly non-atomic and can leave partially modified or sparse files. Retry state lives in pacers and OAuth token renewer side effects.

## Dependencies And Integration Points
The file depends on HiDrive DTO/query helpers, rclone pacer/rest/accounting/fserrors/ranges/readers, and `golang.org/x/sync` errgroup/semaphore. Top-level backend methods in `hidrive.go` compose these helpers for rclone interfaces.

## Risks And Test Signals
`uploadFileChunked` and `updateFileChunked` can create sparse files and partially update existing content when chunks fail. `UploadConcurrency` less than one can deadlock because it becomes the semaphore capacity. `createDirectories` does not roll back parents on later failure. `cachedReader` may buffer whole chunks for retryability. `patchFile` retries HTTP 423 locks. Tests should cover pagination boundaries, 401 token expiry, 404/409 error translation, recursive mkdir partial failures, chunk read errors versus upload errors, continuous-range calculation, and sparse/truncate behavior.
