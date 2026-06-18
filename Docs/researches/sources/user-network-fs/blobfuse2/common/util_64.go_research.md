# sources/user-network-fs/blobfuse2/common/util_64.go
## sources/user-network-fs/blobfuse2/common/util_64.go

Purpose: provides 64-bit architecture assignment for `syscall.Statfs_t.Frsize`.

Important API/function: `SetFrsize(st *syscall.Statfs_t, v uint64)` under build tag `amd64 || arm64`.

Control flow: casts the provided `uint64` to `int64` and assigns it to `st.Frsize`.

State and persistence: mutates only the passed `Statfs_t` struct in memory.

Dependencies/integration: build tags and `syscall`. Selected for common 64-bit Linux targets used by blobfuse2.

Risks: very large `uint64` values above `math.MaxInt64` wrap when cast to `int64`; there is no clamp on 64-bit builds. This is probably acceptable for realistic filesystem fragment sizes but is not guarded.

Test signals: `util_test.go TestSetFrsize` validates assigning `4096` on the active 64-bit build.
