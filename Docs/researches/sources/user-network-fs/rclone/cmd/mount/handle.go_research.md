# sources/user-network-fs/rclone/cmd/mount/handle.go

Purpose: Linux-only bazil FUSE file handle wrapper around `vfs.Handle`.

Important APIs/types: `FileHandle` embeds `vfs.Handle` and implements `HandleReader`, `HandleWriter`, `HandleFlusher`, and `HandleReleaser`.

Control flow: `Read` calls `ReadAt` into the FUSE response slice and treats `io.EOF` as successful short read. `Write` calls `WriteAt` and returns byte count. `Flush` sends buffered writes to VFS; `Release` closes the handle. All errors pass through package `translateError`.

State/persistence: handle operations may read, write, flush, and release remote object content through the VFS cache layer. Dependencies are bazil fuse and VFS. Risks include repeated flush semantics, ignored release errors by kernel, and backend writeback failures surfacing late. Test coverage comes through mount/VFS integration rather than unit tests.
