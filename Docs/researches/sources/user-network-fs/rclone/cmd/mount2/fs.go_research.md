# sources/user-network-fs/rclone/cmd/mount2/fs.go

Purpose: go-fuse v2 top-level FS wrapper around rclone VFS.

Important APIs/types: `FS` holds `*vfs.VFS`, underlying `fs.Fs`, and mount options. `Root`, `SetDebug`, `getMode`, `setAttr`, `setAttrOut`, `setEntryOut`, and `translateError` are central helpers.

Control flow: `Root` wraps VFS root with `newNode`. Attribute helpers convert Go `os.FileInfo` mode/time/size to go-fuse `Attr`/`EntryOut` with mount attr timeouts. `translateError` maps VFS and fs sentinel errors to syscall errno values, returning `EIO` for unknown errors after logging.

State/persistence: owns VFS references only. Dependencies are go-fuse v2, mountlib, fserrors, VFS. Risks include mode conversion for symlinks/special files and incomplete error mapping. Test signal comes from mount2 integration tests.
