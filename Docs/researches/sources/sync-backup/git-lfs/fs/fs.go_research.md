<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/fs/fs.go -->
# sources/sync-backup/git-lfs/fs/fs.go

## Research

`fs.go` models local LFS storage. `Filesystem` stores Git storage dir, LFS storage dir, reference object dirs, cached object/tmp/log dirs, repository permissions, and a mutex. It exposes object enumeration/existence/pathing, path decode helpers, repository permissions, object reference paths, lazy directory creation, cleanup, constructor `New`, alternate resolution, worktree/common-dir handling, and Git redirect file parsing.

Control flow maps OIDs to `objects/aa/bb/<oid>`, treats the empty SHA-256 object as `os.DevNull`, decodes quoted octal paths, reads `GIT_ALTERNATE_OBJECT_DIRECTORIES` and `.git/objects/info/alternates`, and resolves `commondir` indirection for worktrees. Persistent effects are directory creation and cleanup deletion. Dependencies include `tools.FastWalkDir`, `tools.MkdirAll`, path utilities, environment, tracer logging, and OS filesystem calls. Risks include OID length assumptions in `ObjectReferencePaths`, `EachObject` ignoring callback errors, path decode byte/string encoding, alternate quoting, symlink/common-dir correctness, and permission propagation. `fs_test.go` covers octal path decoding and executable/non-executable permissions.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/fs/fs.go -->
