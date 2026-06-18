<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/record/record.go -->
# sources/user-network-fs/bazil-fuse/fs/fstestutil/record/record.go

Purpose: suite of recorder helper types for tests to capture FUSE requests and handler calls.

Important APIs, types, and functions: includes `Writes`, `Counter`, `MarkRecorder`, `Flushes`, `Recorder`, `RequestRecorder`, and request-specific recorders for setattr, fsync, mkdir, symlink, link, mknod, open, xattr operations, and create.

Control flow: handler methods copy request structs, sanitize hard-to-reproduce headers through `RecordRequest`, sometimes deep-copy byte slices, store values under locks, and generally return simple errors or success suitable for test assertions.

State and persistence behavior: state is in-memory counters, buffers, and last-recorded requests. No disk persistence.

Dependencies and integration points: implements many `fs.Node*` and `fs.Handle*` interfaces and uses `fuse.ErrNoXattr` and syscall errors.

Risks and test signals: shallow copies can be unsafe for reused buffers, so `Setxattr` deep-copies xattr data. Tests use recorded zero values to detect missing calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/record/record.go -->
