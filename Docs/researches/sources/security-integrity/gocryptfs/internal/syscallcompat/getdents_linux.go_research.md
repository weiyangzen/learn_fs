# sources/security-integrity/gocryptfs/internal/syscallcompat/getdents_linux.go

Purpose: Portable and security-conscious syscall wrapper code or tests for dirfd-relative operations, no-follow behavior, credentials, xattrs, directory reads, rename flags, EINTR handling, and platform differences.

Important APIs and types: build tags: linux; package `syscallcompat`; functions/tests `getdents`, `getdentsName`, `dtUnknownWarn`, `convertDType`; constants `sizeofDirent`, `maxReclen`; key imports `bytes`, `sync`, `syscall`, `unsafe`, `golang.org/x/sys/unix`, `github.com/hanwen/go-fuse/v2/fuse`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem centralizes syscall details so higher-level FUSE code can use safer defaults such as `O_CLOEXEC`, no-follow lookup, EINTR retry, and platform-specific fallbacks. Directory entry conversion must handle dot entries, deleted-in-flight names, unknown d_type values, and corrupt dirent lengths without crashing the mount.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `bytes`, `sync`, `syscall`, `unsafe`, `golang.org/x/sys/unix`, `github.com/hanwen/go-fuse/v2/fuse`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior; some checks are timing-sensitive.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
