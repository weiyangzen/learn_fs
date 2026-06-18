# sources/user-network-fs/rclone/cmd/mount2/file.go

Purpose: go-fuse v2 file handle adapter for rclone VFS handles.

Important APIs/types: `FileHandle` with `vfs.Handle` and `*FS`; `newFileHandle`; implementations for `FileHandle`, `FileReader`, `FileWriter`, `FileFlusher`, `FileReleaser`, `FileFsyncer`, `FileGetattrer`, and `FileSetattrer`.

Control flow: `Read`/`Write` call VFS `ReadAt`/`WriteAt`, converting EOF to success for short reads. `Flush`, `Release`, and `Fsync` forward to VFS flush/release/sync. `Getattr` and `Setattr` populate go-fuse attr structs; `Setattr` supports truncate and mtime on the underlying node.

State/persistence: handle operations read and mutate remote content through VFS cache/writeback. Dependencies are go-fuse v2 and VFS. Risks include late write errors on flush/fsync, attribute updates on handle vs node paths, and kernel ignoring release errors.
