<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/block/block.go -->
# Research: sources/user-network-fs/gcsfuse/internal/block/block.go

Purpose: memory-backed block abstraction for read/write buffering, implemented with mmap-backed byte slices.

Important APIs/types/functions: `Block` combines `io.ReadSeeker`, `io.Writer`, `GenBlock`, `Size`, and `Cap`; `memoryBlock` stores `buffer` and `readSeek`; `createBlock` allocates anonymous private mmap memory.

Control flow: `Write` appends data until capacity; `Read` copies from `readSeek` and returns EOF at the end; `Seek` supports start/current/end with bounds checks; `Reuse` clears data and read position; `Deallocate` munmaps the full capacity and nils the buffer.

State and persistence: state is process memory only, backed by OS virtual memory. Deallocation releases mmap resources; blocks returned to pools are reused after reset.

Dependencies: `syscall.Mmap/Munmap`, `io`, and external pool lifecycle management.

Risks: double deallocation or using a block after deallocation causes errors/panics or memory corruption risk. Large block sizes can fail mmap. The implementation is not synchronized.

Test signals: `block_test.go` covers writes, reads, seeking, capacity errors, reuse, and deallocation behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/block/block.go -->
