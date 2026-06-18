
# sources/user-network-fs/rclone/backend/hdfs/fs.go

## Purpose
This file implements the filesystem-level HDFS backend for non-Plan 9 builds. It creates the HDFS client, wires Kerberos or simple-user authentication, exposes rclone `fs.Fs` methods, and implements directory, object, move, purge, and quota operations against `github.com/colinmarc/hdfs/v2`.

## Important APIs, Types, And Control Flow
`Fs` stores remote name, root, parsed `Options`, global config, HDFS client, feature set, and pacer. `NewFs` parses config, builds `hdfs.ClientOptions`, optionally loads Kerberos credentials with `getKerberosClient`, initializes the client, and returns `fs.ErrorIsFile` if the configured root is a file. `List`, `NewObject`, `Put`, `Mkdir`, `Rmdir`, `Purge`, `Move`, `DirMove`, and `About` implement the rclone backend surface. `ensureDirectory` and `ensureFile` translate HDFS stat results to rclone `fs.ErrorDirNotFound` and `fs.ErrorObjectNotFound`.

## State And Persistence
State is mainly the live HDFS client and root path. Persistent effects happen directly in HDFS: mkdirs, removes, recursive removes, renames, writes through object update, and quota reads via `StatFs`. `realpath` combines configured root and remote path through `xPath` and the configured encoder.

## Dependencies And Integration Points
The backend integrates with the HDFS Go client, gokrb5 config/credential cache loading, rclone encoders, pacer, and optional rclone interfaces `Purger`, `PutStreamer`, `Abouter`, `Mover`, and `DirMover`. Kerberos uses `KRB5_CONFIG` and `KRB5CCNAME`, accepting only file credential caches.

## Risks And Test Signals
`Move` relies on HDFS `Rename` behavior that overwrites because the library hard-codes overwrite. `DirMove` only checks destination existence, not detailed source type after stat failure. HDFS path encoding and root joining should be tested with leading slash, colon, and invalid UTF-8 cases. Kerberos has environment-dependent risks around unsupported credential cache types. Integration tests need a real `TestHdfs:` remote and should cover root-as-file, empty-directory support, quota reporting, same-remote moves, recursive purge, and non-empty `Rmdir`.
