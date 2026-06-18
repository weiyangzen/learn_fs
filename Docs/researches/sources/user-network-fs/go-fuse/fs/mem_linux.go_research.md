# sources/user-network-fs/go-fuse/fs/mem_linux.go

Purpose: Linux-specific helper for in-memory fallocate behavior.

Important API: `keepSizeMode(mode uint32) bool` returns whether `unix.FALLOC_FL_KEEP_SIZE` is set.

Control flow/state: no state; used by `MemRegularFile.Allocate` to decide whether allocation should grow capacity without changing visible size.

Dependencies/integration: Linux build uses `golang.org/x/sys/unix`. Risks are minimal; non-Linux implementations must provide compatible behavior. Test signal is indirect through fallocate/memory-file behavior.
