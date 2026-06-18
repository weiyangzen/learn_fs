# sources/user-network-fs/blobfuse2/component/block_cache/block.go

Purpose: `block.go` defines the core in-memory block buffer type used by the BlobFuse2 block cache and helper state for block upload/download tracking.

Important APIs, types, and functions: Block flags include `BlockFlagFresh`, `BlockFlagDownloading`, `BlockFlagUploading`, `BlockFlagDirty`, `BlockFlagSynced`, and `BlockFlagFailed`. Status channel values include `BlockStatusDownloaded`, `BlockStatusUploaded`, `BlockStatusDownloadFailed`, and `BlockStatusUploadFailed`. `Block` stores offset, block id, readiness channel, `common.BitMap64` flags, memory-mapped data, and a list node. `blockInfo` records remote block IDs, commit state, and size. Methods include `AllocateBlock`, `Delete`, `ReUse`, `Uploading`, `Ready`, `Unblock`, `Dirty`, `NoMoreDirty`, `IsDirty`, `Failed`, and `IsFailed`.

Control flow: `AllocateBlock` validates size, uses `syscall.Mmap` to allocate an anonymous private read/write buffer, initializes a fresh block with id `-1`, and deliberately leaves `state` nil until reuse. `ReUse` resets identity, offset, flags, and creates a buffered readiness channel. Download/upload code calls `Ready` once with a status, and the first reader closes the channel through `Unblock` so later readers do not block.

State and persistence behavior: Block data is held in an mmap-backed byte slice and must be released with `Delete`, which calls `syscall.Munmap` and nils the data. Flags encode dirty, synced, failed, and transfer state in memory. The readiness channel coordinates goroutines but is not persisted. `blockInfo` mirrors staged/committed remote block-list state for later commits.

Dependencies and integration points: This file depends on Go `container/list`, `syscall`, and BlobFuse2 `common.BitMap64`. `block_cache.go` uses `Block` instances in handle cooked/cooking lists, block pools, download/upload workers, disk cache reads, and commit-block generation.

Risks: Callers must avoid using a block after `Delete` because `data` is nil and the mmap is gone. Closing `state` more than once would panic, so ownership of `Unblock` matters. `Ready` silently drops a status if the buffered channel is full; the design assumes one status per transfer. `AllocateBlock` converts `uint64` size to `int`, so extremely large sizes can overflow on unsupported configurations before `Mmap`.

Test signals: No direct tests are in this file. Behavior is indirectly covered by block cache tests elsewhere and by integration paths in `datalake_test.go` that exercise block staging/flush semantics. Missing direct coverage includes mmap allocation failure, double `Delete`, double `Unblock`, status drop behavior, and flag transitions in isolation.
