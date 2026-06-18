# sources/user-network-fs/blobfuse2/common/util_32.go
## sources/user-network-fs/blobfuse2/common/util_32.go

Purpose: provides ARM 32-bit-specific assignment for `syscall.Statfs_t.Frsize`.

Important API/function: `SetFrsize(st *syscall.Statfs_t, v uint64)` under build tag `arm`.

Control flow: if the requested value exceeds `math.MaxInt32`, it clamps to `MaxInt32` to avoid silent truncation; otherwise it converts the value to `int32` and assigns `st.Frsize`.

State and persistence: mutates only the passed `Statfs_t` struct in memory.

Dependencies/integration: build tags, `math`, and `syscall`. This function shares the same public name as the 64-bit implementation, selected by architecture at build time.

Risks: only the ARM build uses this clamping behavior; callers relying on exact large values get saturation instead. The general `util_test.go` assertion expects `int64` field behavior and is primarily suited to 64-bit builds, so 32-bit-specific clamping needs separate architecture-aware coverage.

Test signals: indirect through `util_test.go TestSetFrsize` when tests run on an ARM 32-bit target, though that test only checks a small value.
