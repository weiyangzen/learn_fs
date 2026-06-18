## sources/user-network-fs/gcsfuse/internal/perms/perms.go

### Purpose
`perms.go` provides a small system helper to obtain the current process UID and GID as unsigned IDs for filesystem ownership logic.

### Important APIs, Types, And Functions
The exported function is `MyUserAndGroup() (uid, gid uint32, err error)`.

### Control Flow
It calls `os.Getuid()` and `os.Getgid()`, checks for negative values, returns an error if either is negative, otherwise casts both to `uint32`.

### State, Persistence, And Dependencies
There is no mutable or persistent state. Dependency is standard `os` plus `fmt` for error construction.

### Integration Points
Mount and inode code can use this helper to default ownership to the current process identity.

### Risks
Negative UID/GID is mostly a non-Unix concern; on platforms where `os.Getuid` is unsupported or returns -1, callers must handle the error. Casting large signed IDs to uint32 assumes OS IDs fit the expected range.

### Test Signals
`perms_test.go` asserts the helper succeeds in the test environment and does not return uint32(-1). It does not simulate negative OS return values.
