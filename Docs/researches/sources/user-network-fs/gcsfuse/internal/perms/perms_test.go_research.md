## sources/user-network-fs/gcsfuse/internal/perms/perms_test.go

### Purpose
`perms_test.go` validates that current UID/GID lookup works in the test environment.

### Important APIs, Types, And Functions
The suite defines `PermsTest`, registers it through testify suite, and runs `MyUserAndGroupNoError`.

### Control Flow
The test calls `perms.MyUserAndGroup`, expects no error, and checks both returned IDs are not `uint32(-1)`.

### State, Persistence, And Dependencies
There is no persistent state. The test depends on the process environment and `testify`.

### Integration Points
This is a smoke test for filesystem ownership defaults on supported systems.

### Risks
The test cannot force the negative-ID error branch because `os.Getuid` and `os.Getgid` are not injectable. It also does not compare against expected IDs from the OS.

### Test Signals
Signal is limited but useful: the helper is callable and returns plausible IDs where the suite runs.
