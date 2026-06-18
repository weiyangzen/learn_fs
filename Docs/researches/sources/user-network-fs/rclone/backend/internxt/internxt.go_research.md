# sources/user-network-fs/rclone/backend/internxt/internxt.go

## Purpose
Implements the main Internxt Drive rclone backend, including configuration, auth-aware retries, directory caching, list/create/delete operations, object download/upload/update, quota reporting, and shutdown.

## Important APIs, Types, and Functions
`Options` defines email/password/mnemonic, hash validation toggle, upload cutoff/chunk sizing/concurrency, and encoding. `Fs` stores root, config mapper, dircache, Internxt SDK config, features, pacer, OAuth token renewer, bridge user/user ID, and auth locking state. `Object` stores remote, file ID, UUID, size, and modtime.

Core methods include `shouldRetry`, `Config`, `NewFs`, `Mkdir`, `Rmdir`, `FindLeaf`, `CreateDir`, `preUploadCheck`, `convertFileMetaToFile`, `List`, `Put`, `Remove`, `NewObject`, `newObjectWithFile`, `About`, `Shutdown`, `Object.Open`, `Object.Update`, `recoverFromTimeoutConflict`, `restoreBackupFile`, and `Object.Remove`.

## Control Flow
`Config` performs a staged login flow: check email, optionally ask for 2FA, perform login, store mnemonic obscured, convert JWT into an OAuth token, save it, and clear temporary 2FA. `NewFs` validates upload sizing, reveals mnemonic, loads token, creates SDK config, fetches user info with retry and 401 re-auth fallback, fills bucket/root/basic auth, starts an OAuth renewer, and initializes `dircache`. If root lookup fails, it probes parent as a possible file root.

Directory operations use `dircache`: `FindLeaf` lists folders by parent UUID, `CreateDir` creates folders and handles conflicts by searching for an existing folder, `Rmdir` verifies no child folders/files before deletion. Listing fetches folders and files separately and converts file plain name/type into rclone remote names.

Uploads use a cautious overwrite strategy. Existing files are renamed to a unique backup before upload. Small files use `buckets.UploadFileStreamAuto`; large or unknown-size files use the multipart chunk writer. Empty-file limit errors map to `fs.ErrorCantUploadEmptyFiles`. Timeout or conflict errors are followed by existence checks to recover metadata when the upload likely succeeded. On success, backup files are deleted; on failure, `restoreBackupFile` tries to rename the backup back.

## State and Persistence
Remote Internxt state includes folders, file metadata, bucket objects, and pending thumbnails. Local state includes dircache mappings, OAuth token renewer, mutable upload options, and auth circuit state. Tokens and mnemonic are persisted in the rclone config mapper. `Shutdown` waits for thumbnail work and stops token renewal.

## Dependencies and Integration Points
Depends on Internxt adapter packages `auth`, `buckets`, `config`, `errors`, `files`, `folders`, and `users`; rclone `fs`, config helpers, `dircache`, `encoder`, `multipart`, `oauthutil`, `pacer`, and `random`. It implements rclone filesystem, object, about, shutdown, and dircache interfaces.

## Risks and Edge Cases
Upload overwrite safety depends on backup rename and restore succeeding; backup deletion failure can leave orphaned files. `preUploadCheck` intentionally treats existence-check errors as no existing file, which can allow conflicts later. `Remove` attempts object delete before folder delete, so ambiguous file/folder names may prefer file semantics. `About` subtracts pointers returned by usage values and assumes both are present. Auth failure circuit breaker can make later transient auth recovery impossible without recreating the Fs.

## Test Signals
`internxt_test.go` provides only generic integration coverage with chunked upload settings. No pure unit tests cover the staged config flow, retry reauth, backup rollback, timeout conflict recovery, or directory cache behavior.
