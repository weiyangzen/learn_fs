## sources/user-network-fs/blobfuse2/component/loopback/loopback_fs.go

Purpose: Implements `internal.Component` against the local filesystem. It is a consumer component useful for tests, local backends, and xload remote simulation.

Important APIs and flow: `Configure` reads `loopbackfs.path`, creates it if missing, and stores the root path. Directory methods map to `os.Mkdir`, `os.Remove`, `os.ReadDir`, `os.Rename`, and optional MD5 calculation in `StreamDir` when consistency mode is enabled. File methods create/open local files, wrap them in `handlemap.Handle`, lock handles for read/write, support `ReadInBuffer` both with and without an open handle, and expose copy, truncate, chmod, chown, symlink, readlink, stat-like `GetAttr`, staged block writes, and commit assembly.

State and persistence: Persistent state is the host directory tree under `lfs.path`. `consistency` toggles MD5 population for streamed files. `StageData` writes temporary files named from object plus sanitized block id; `CommitData` assembles staged data at block offsets and removes stage files.

Dependencies and integration: Uses `internal` option structs, `handlemap`, `common.GetMD5`, and POSIX file operations. It registers as `loopbackfs`.

Risks: Path joining does not guard against traversal. `ReadInBuffer` returns `(0,nil)` for open errors without a handle. `CommitData` defaults `BlockSize` to zero unless caller sets it, making offsets collapse. Tests cover core filesystem paths and block commit basics.
