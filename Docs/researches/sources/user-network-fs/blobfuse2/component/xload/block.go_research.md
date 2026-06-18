## sources/user-network-fs/blobfuse2/component/xload/block.go

Purpose: Defines the reusable memory block used by xload to stage chunk data during parallel downloads.

Important APIs and flow: `Block` records pool index, file offset, valid length, storage block id, and a byte slice backed by memory mapping. `AllocateBlock` rejects zero size, creates anonymous private read/write memory with `syscall.Mmap`, and returns a `Block` whose `Data` points at that mapping. `Delete` unmaps `Data` with `syscall.Munmap` and nils the slice. `ReUse` resets metadata before returning the block to active use.

State and dependencies: State is in the mmap allocation and metadata fields. It depends directly on Linux/POSIX mmap semantics through `syscall`.

Risks: Manual mmap lifecycle means double-free, deleting non-mmap byte slices, or forgetting `Delete` can leak or fail. `ReUse` does not clear the actual data bytes, so consumers must respect `Length`/transfer counts and not read stale content. Tests cover zero, normal, large, huge allocation failure, invalid delete, and metadata reuse.
