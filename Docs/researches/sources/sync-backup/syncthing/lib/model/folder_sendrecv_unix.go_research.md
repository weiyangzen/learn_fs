# sources/sync-backup/syncthing/lib/model/folder_sendrecv_unix.go

Purpose: this non-Windows implementation provides `(*sendReceiveFolder).syncOwnership` for Unix-like platforms. It applies owner and group metadata from `protocol.FileInfo.Platform.Unix` to an on-disk path through the folder's mtime-aware filesystem wrapper.

Important API: `syncOwnership(file *protocol.FileInfo, path string) error` is the only function. It returns nil when no Unix platform ownership data is present. When metadata exists, it converts numeric UID and GID to strings, optionally resolves `OwnerName` and `GroupName` through `os/user`, and calls `f.mtimefs.Lchown(path, uid, gid)`. The use of `Lchown` is important because ownership updates must apply to the path itself rather than following symlinks.

Control flow: the function first checks `file.Platform.Unix == nil` and exits early. It initializes fallback owner and group strings from `UID` and `GID`. If owner or group names are populated, it attempts a name lookup; successful lookups with non-empty IDs replace the numeric fallback. Lookup failures are intentionally ignored, preserving the numeric identifiers from the remote metadata. Finally, the resolved string IDs are passed to the filesystem layer.

State and persistence behavior: there is no in-memory state. The only persistent effect is filesystem metadata mutation through `mtimefs.Lchown`. The code does not update database state directly; any index update or scan reconciliation happens elsewhere in the send/receive pipeline.

Dependencies and integration points: it depends on Go's `os/user` package, `strconv`, and Syncthing's `protocol.PlatformData`. Its primary integration point is the `sendReceiveFolder` platform-data application path. It also relies on the configured filesystem implementation supporting `Lchown`; fake filesystems in tests can emulate ownership, while real filesystems may require privileges.

Risks: user and group name resolution is host-local and may not match the source device. The numeric fallback is necessary for portability but may still fail if the process lacks permission. Because lookup errors are swallowed, troubleshooting depends on the eventual `Lchown` error. The path must already be safely resolved by callers; this function deliberately uses link-aware ownership mutation but does not perform path validation.

Test signals: ownership behavior is indirectly covered by send/receive tests such as parent-owner copy tests and by platform-data tests that ensure `setPlatformData` can run against a filesystem. Direct Unix owner-name resolution edge cases are not tested here.
