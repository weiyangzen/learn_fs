# sources/user-network-fs/rclone/backend/box/upload.go

## Purpose
Implements Box multipart upload sessions for objects above the upload cutoff: create session, upload digest-checked parts, commit with retry handling, abort on failure, and update object metadata.

## Important APIs, types, and functions
`createUploadSession` chooses new-file or existing-version upload-session endpoints. `sha1Digest` formats RFC3230-style SHA1 digest headers. `uploadPart` sends one chunk with `Content-Range` and `Digest`. `commitUpload` posts ordered parts and timestamps, handles `202 Accepted`, `Retry-After`, and transient `parts_mismatch`, and retries up to `CommitRetries`. `abortUpload` cancels sessions. `uploadMultipart` orchestrates the full flow.

## Control flow
`uploadMultipart` starts a session, uses Box's part size, defers abort on error, unwraps accounting, reads chunks sequentially into byte slices, updates whole-file SHA1, uploads parts concurrently under `uploadToken`, then commits ordered part descriptors and stores returned metadata.

## State and persistence
Remote state includes upload session, uploaded parts, final file/version, or aborted session. Local state includes session response, part buffers, ordered part slice, SHA1 hash, error channel, wait group, and upload tokens.

## Dependencies and integration points
Called from `Object.Update` in `box.go`. Uses Box API types, rclone accounting, rest/pacer retry handling, and `atexit.OnError`.

## Risks
Requires known size for multipart. Memory usage scales with Box part size and active goroutines. Commit may exhaust retries during Box consistency delays. Abort only runs on returned errors, so process death can leave sessions. There are no direct unit tests for digest formatting or commit retry behavior.

## Test signals
Covered indirectly by generic Box integration when test file sizes cross the upload cutoff.
