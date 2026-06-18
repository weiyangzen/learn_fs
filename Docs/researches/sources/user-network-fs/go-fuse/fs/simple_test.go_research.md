## sources/user-network-fs/go-fuse/fs/simple_test.go

Purpose: broad integration suite for the modern `fs` loopback implementation and mount lifecycle.

Important APIs/types/functions: `testCase`, `testOptions`, and `newTestCase` set up backing and mount directories, `NewLoopbackRoot`, `NewNodeFS`, and `fuse.NewServer`. Tests cover basic stat/remove, executable files, fd leaks, notify entry/prune, readdir stress, statfs, getattr/close races, unsupported mknod, POSIX matrix, disabled splice, direct I/O, fsstress, stale hardlinks, parallel mounts, handleless create, and lchown on dangling symlinks.

Control flow: most tests mount a loopback FS, mutate either the backing directory or mount path, then assert kernel-visible behavior. Stress tests fan out goroutines and external `ls` loops. POSIX tests delegate to `posixtest.All`.

State and persistence: durable test state lives in temp backing directories; `rawBridge` tracks open files and inode state. Caches are explicitly toggled through attr and entry timeouts.

Dependencies and integration: integrates high-level `fs`, raw `fuse.Server`, `LoopbackNode`, `posixtest`, `unix` syscalls, and kernel mount options such as direct mount, splice, locks, and idmapped mount.

Risks and test signals: this is a primary regression file for deadlocks, descriptor leaks, stale inode reuse, cache invalidation, and mount concurrency. Some tests are environment-sensitive and may skip or fail depending on filesystem type, privileges, or FUSE support.
