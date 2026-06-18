<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/spawntest/spawntest.go -->
# sources/user-network-fs/bazil-fuse/fs/fstestutil/spawntest/spawntest.go

Purpose: subprocess helper framework for tests that need client operations outside the main test process.

Important APIs, types, and functions: defines `Registry`, `Register`, `AddFlag`, `RunIfNeeded`, `Helper`, `Helper.Spawn`, `Control`, `Close`, `Signal`, `HTTP`, and `JSON`.

Control flow: tests register named HTTP handlers, add the internal helper flag in `TestMain`, and spawn the same test binary with an inherited Unix listener on fd 3. Helper mode serves HTTP on that listener; parent mode controls it with an httpunix client.

State and persistence behavior: registry maps names to handlers; each spawned helper owns a temp dir, Unix socket, process, and HTTP client until `Close`.

Dependencies and integration points: uses `net`, `os/exec`, `testing.TB`, `github.com/tv42/httpunix`, and `httpjson`.

Risks and test signals: process cleanup depends on `Close`; startup errors call `t.Fatalf`. Duplicate helper names panic, catching test setup mistakes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/spawntest/spawntest.go -->
