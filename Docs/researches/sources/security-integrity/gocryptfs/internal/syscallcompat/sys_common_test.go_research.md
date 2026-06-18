# sources/security-integrity/gocryptfs/internal/syscallcompat/sys_common_test.go

Purpose: Portable and security-conscious syscall wrapper code or tests for dirfd-relative operations, no-follow behavior, credentials, xattrs, directory reads, rename flags, EINTR handling, and platform differences.

Important APIs and types: package `syscallcompat`; functions/tests `TestReadlinkat`, `TestOpenat`, `TestRenameat`, `TestUnlinkat`, `TestFchmodatNofollow`, `symlinkCheckMode`, `TestSymlinkat`, `TestMkdirat`, `TestFstatat`, `BenchmarkLgetxattr`; key imports `bytes`, `os`, `runtime`, `syscall`, `testing`, `golang.org/x/sys/unix`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem centralizes syscall details so higher-level FUSE code can use safer defaults such as `O_CLOEXEC`, no-follow lookup, EINTR retry, and platform-specific fallbacks. Extended attribute helpers normalize Linux/macOS buffer sizing differences and avoid ERANGE retry loops by converting oversize values to overflow errors.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `bytes`, `os`, `runtime`, `syscall`, `testing`, `golang.org/x/sys/unix`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior; some checks are timing-sensitive.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
