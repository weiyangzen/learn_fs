
# sources/user-network-fs/rclone/backend/jottacloud/jottacloud.go

## Purpose
Implements the rclone Jottacloud backend, including backend registration, interactive configuration, OAuth/token migration, JFS/XML and JSON API clients, object metadata, listing, uploads, server-side copy/move, trash cleanup, quota, public links, and shutdown of token renewal.

## Important APIs, Types, And Control Flow
Key types are `Options`, `Fs`, `Object`, and the internal `service` descriptor for white-label OAuth providers. `Config` is a state machine covering standard personal login tokens, traditional OAuth, legacy password/OTP auth, and optional device/mountpoint selection/creation. `NewFs` builds OAuth clients, REST clients, pacer, features, user endpoints, and root-file detection. Filesystem methods include `List`, `ListR`, `Put`, `Mkdir`, `Rmdir`, `Purge`, `Copy`, `Move`, `DirMove`, `PublicLink`, `About`, `UserInfo`, and `CleanUp`. Object methods manage MD5, times, metadata, range reads, allocation/resumable upload, and soft/hard delete.

## State And Persistence
Persistent state lives in rclone config keys such as token URL, client ID/secret, OAuth token, config version, device, and mountpoint. Runtime state includes REST clients, pacer backoff, cached object metadata, upload temp files from `readMD5`, and a background token renewer. Remote persistence is through Jottacloud file, trash, share, metadata timestamp, and deduplicated upload allocation APIs.

## Dependencies And Integration Points
Depends on rclone `fs`, `oauthutil`, `rest`, `pacer`, `encoder`, `accounting`, hashes, and Jottacloud API structs. It integrates with rclone optional interfaces including `Purger`, `Copier`, `Mover`, `DirMover`, `ListRer`, `PublicLinker`, `Abouter`, `UserInfoer`, `CleanUpper`, `Shutdowner`, `MimeTyper`, and `Metadataer`.

## Risks And Test Signals
High-risk paths include legacy token refresh body rewriting, config-version compatibility, white-label provider endpoint drift, XML liststream count validation, trash-only filtering, hard delete semantics, MD5 buffering to disk for large files, upload resume offsets, no-versions delete-before-upload, and metadata timestamp parsing. Tests should cover config branches with mocked REST, liststream parsing, `readMD5`, allocation/dedupe/resume upload, metadata copy/move, trash-only behavior, root-as-file, and token renewer shutdown.
