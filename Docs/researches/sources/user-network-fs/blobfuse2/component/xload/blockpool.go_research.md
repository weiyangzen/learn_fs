## sources/user-network-fs/blobfuse2/component/xload/blockpool.go

Purpose: Provides a bounded pool of preallocated mmap `Block` objects for xload, split into regular and high-priority capacity.

Important APIs and flow: `NewBlockPool` validates nonzero block size/count, reserves 10% of blocks for `priorityCh`, preallocates every block via `AllocateBlock`, and returns nil on allocation failure. `GetBlock(priority)` tracks waiters and delegates to `mustGet` for priority requests or `tryGet` for regular requests. `tryGet` waits only on regular blocks; `mustGet` can consume priority or regular blocks. Both honor context cancellation and call `ReUse`. `Release` preferentially fills `priorityCh`, then regular, then deletes overflow blocks. `Terminate` closes channels and drains them through `releaseBlocks`.

State and dependencies: State lives in buffered channels, `waitLength`, `blockSize`, `maxBlocks`, and cancellation context. It integrates with splitter scheduling and stats usage reporting.

Risks: `releaseBlocks` reads until channel closure returns nil; this assumes no nil block values. Closing while other goroutines call `GetBlock`/`Release` can panic. For small pool sizes, 10% priority truncates to zero. Tests cover allocation, usage, exhaustion, release, and termination.
