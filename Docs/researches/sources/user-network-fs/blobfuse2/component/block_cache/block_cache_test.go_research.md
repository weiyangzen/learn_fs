# sources/user-network-fs/blobfuse2/component/block_cache/block_cache_test.go

## Purpose

`block_cache_test.go` is the main integration-style unit suite for the Blobfuse2 block cache component. It exercises configuration, read prefetching, disk-cache spillover, block-list validation, write-back upload, sparse writes, overwrite races, committed and uncommitted block handling, lazy write, stream-to-block-cache compatibility, and strong consistency metadata.

## Important APIs, Types, and Functions

The suite defines `blockCacheTestSuite`, `testObj`, `setupPipeline`, `cleanupPipeline`, `randomString`, `getFakeStoragePath`, `getTestFileName`, and `computeMD5`. Tests construct a loopback-backed pipeline using `loopback.NewLoopbackFSComponent`, `NewBlockCacheComponent`, and the component lifecycle methods `Configure`, `Start`, and `Stop`. Most assertions target `BlockCache` methods including `CreateFile`, `OpenFile`, `ReadInBuffer`, `WriteFile`, `FlushFile`, `ReleaseFile`, `SyncFile`, `RenameFile`, `DeleteFile`, `RenameDir`, `DeleteDir`, `StatFs`, `validateBlockList`, `stageBlocks`, and `checkDiskUsage`.

## Control Flow

Each test builds a temporary fake storage root and disk cache root, loads YAML-like config through `config.ReadConfigFromReader`, wires block cache above loopback storage, and starts both components. Read tests create files directly in fake storage, open them through block cache, then read sequential or random offsets to drive `getBlock`, prefetch, and disk/memory eviction paths. Write tests create or open handles through block cache, write byte ranges at aligned and unaligned offsets, flush or release the handle, and compare storage size or MD5 output to a reference local file. Race-focused tests deliberately stage blocks, rewrite already staged blocks, read blocks while writes are pending, and validate that the cooked/cooking lists settle correctly.

## State and Persistence Behavior

The test suite validates state held in temporary directories, handle buffer lists, handle dirty flags, block maps, disk cache files named with block suffixes, xattrs for strong consistency, and global `common.IsStream`. Cleanup stops components and removes temporary directories. Several tests rely on asynchronous cleanup or upload behavior and use sleeps, polling, or release operations to wait for state transitions.

## Dependencies and Integration Points

Dependencies include `common`, `config`, `log`, `loopback`, `internal`, `memory`, `testify`, and operating-system tools such as `nproc`, `free`, and `df`. The tests integrate block cache with the loopback component rather than a cloud backend, giving broad component-level signal without Azure service calls.

## Risks and Edge Cases

The suite is environment-sensitive: free memory, disk size, permissions, xattr support, external shell command output, and timing can affect results. The 50 GiB mmap failure test and long sleeps can be brittle on constrained systems. The tests cover many high-risk cases: invalid prefetch/memory/disk config, temp-path conflicts, disk-threshold decisions, sparse file holes, partial block overwrites, block index limits, failed block downloads, reads of staged blocks, uncommitted block validation, prefetch-disabled behavior, lazy write deferral, and strong consistency xattr refresh.

## Test Signals

Passing this suite gives strong confidence that block cache preserves data across reads, random writes, sparse writes, flush/release sequences, and local disk cache interactions. It also signals that read prefetch does not overgrow handle block lists, that write-back can recover from staged or committed block overlap, and that block cache still interoperates with stream component compatibility settings.
