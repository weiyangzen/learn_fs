# sources/user-network-fs/rclone/backend/smb/smb.go

## Purpose

`smb.go` implements the rclone SMB/CIFS backend. It maps rclone filesystem operations onto `go-smb2` share, file, directory, quota, and rename APIs.

## Important APIs, Types, and Functions

`Options` covers host, port, user/password/domain/SPN, Kerberos settings, special-share hiding, case sensitivity, idle timeout, and encoding. `Fs` stores backend state plus connection pool/session tracking. `Object` wraps remote path and `os.FileInfo`. Core methods include `NewFs`, `List`, `NewObject`, `Mkdir`, `Rmdir`, `Put`, `PutStream`, `Move`, `DirMove`, `About`, `OpenWriterAt`, `Shutdown`, `ensureDirectory`, path conversion helpers, and object `Open`, `Update`, `SetModTime`, `Remove`.

## Control Flow

Initialization parses config, sets feature flags including bucket/share semantics and partial uploads, starts an idle drain timer, and checks whether a non-directory root is a file. Paths are split into share and in-share path with `bucket.Split`. Listing at server root enumerates share names and hides `$` shares when configured; listing inside a share reads directory entries. Upload creates parents, opens/truncates the SMB file, streams data, closes it, and sets modtime. Reads borrow a connection, open the file, seek for range/seek options, and return a `boundReadCloser` that returns the connection on close. Server-side move/dir move require source and destination on the same share. `OpenWriterAt` pre-creates/truncates the file and returns a pooled random-access writer.

## State and Persistence Behavior

In-memory state includes connection pool, idle timer, active session count, and cached object stat info. Persistent effects occur on the SMB server: file contents, directories, renames, deletes, and timestamps.

## Dependencies and Integration Points

It depends on rclone `fs`, `bucket`, `encoder`, `pacer`, `readers`, and helper files `connpool.go`, `filepool.go`, and `kerberos.go`. It implements rclone optional interfaces for streaming uploads, mover, dir mover, usage, shutdown, and writer-at support.

## Risks and Edge Cases

The file contains duplicated unreachable returns in `String`. `DirMove` stats `dstPath` without converting to Samba path, unlike most operations. Root/share boundary cases return `fs.ErrorIsDir` or no-op directory operations. Active-session accounting must stay balanced to avoid premature or blocked drains. Mandatory unsupported open options are logged but not rejected in `Open`.

## Test Signals

Integration tests cover NTLM and Kerberos remotes. Unit tests cover `isPathDir`; filepool and kerberos helpers have separate unit tests. Strong signals include parallel reads/writes, random-access writer correctness, same-share move restrictions, share-root listing, special-share hiding, and timestamp preservation.
