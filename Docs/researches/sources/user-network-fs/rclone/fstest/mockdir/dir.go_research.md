
# sources/user-network-fs/rclone/fstest/mockdir/dir.go

Purpose: package `mockdir` provides the smallest useful `fs.Directory` test double. Its only public API is `New(name string) fs.Directory`, which returns `fs.NewDir(name, time.Time{})`.

Important APIs/types/functions: `New` is the complete surface. It preserves the remote name and uses the zero time as directory modtime, leaving richer metadata behavior to callers or other mocks.

Control flow: there is no branching beyond constructing and returning the directory value.

State/persistence: no package state and no persistence. Each call returns an independent directory object.

Dependencies/integration: depends on rclone `fs.NewDir` and Go `time`. It integrates with tests that need directory entries in `fs.DirEntries` without standing up a backend.

Risks: zero modtime may be unsuitable for tests that assert directory timestamp behavior. It does not exercise optional directory metadata or set-modtime interfaces.

Test signals: no local tests in this file; correctness is indirectly signaled by tests that consume mock directory entries.
