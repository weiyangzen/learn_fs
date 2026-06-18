## sources/sync-backup/restic/internal/fuse/fuse_test.go

Purpose: integration and unit coverage for the Unix FUSE implementation. The tests build in-memory test repositories, create snapshots, and exercise file reads, directory attrs, UID/GID presentation, stable FUSE node caching, block counts, hard-link inode generation, symlink xattrs, and inode benchmarks.

Important APIs and helpers: `testRead` adapts `fs.HandleReader` to synthetic `fuse.ReadRequest`; `firstSnapshotID`, `loadFirstSnapshot`, and `loadTree` pull snapshot/tree data from repository fixtures. `TestFuseFile` constructs a `data.Node`, opens it through `newFile`, and validates random reads against concatenated blob contents. `TestFuseDir`, `TestTopUIDGID`, and `testTopUIDGID` validate attribute propagation from `data.Node` and mount config. `testStableLookup` verifies `treeCache` object identity until `Forget`. `TestBlocks`, `TestFileAttrNlink`, `TestInodeFromNode`, and `TestLink` cover stat details, POSIX compatibility, inode rules, and xattr lookup.

Control flow and state: tests create repository state with `repository.TestRepository` and `data.TestCreateSnapshot`, load repository indexes where needed, and then instantiate FUSE nodes directly rather than mounting a kernel filesystem. Cache-sensitive checks call `Forget` to force eviction and confirm a later lookup constructs a new node object.

Dependencies and integration points: this file exercises `bloblru`, `data`, `repository`, `restic`, `anacrolix/fuse`, `anacrolix/fuse/fs`, and restic test helpers. It reaches unexported FUSE constructors, so it is tightly coupled to the package internals.

Risks and test signals: the suite catches regressions that would break user-visible mounted filesystem behavior, especially block accounting, UID/GID choice, hard-link inode stability, and xattr forwarding. It does not mount through the OS FUSE driver, so kernel integration, permissions enforcement, and platform-specific filesystem behavior remain outside this file.
