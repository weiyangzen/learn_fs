## sources/user-network-fs/blobfuse2/component/xload/block_test.go

Purpose: Unit tests for xload `Block` mmap allocation, deletion, and reuse.

Important APIs and flow: `TestBlockAllocate` checks zero-size rejection and a successful small allocation/delete. `TestBlockAllocateBig` confirms a 100 MiB allocation exposes the expected capacity. `TestBlockAllocateHuge` expects a 50 GiB mmap to fail. `TestBlockFreeNilData` and `TestBlockFreeInvalidData` verify delete error behavior for nil or non-mmap data. `TestBlockResuse` validates metadata reset.

State and dependencies: Tests exercise actual mmap/munmap behavior through `syscall`, so behavior is OS and overcommit dependent.

Risks and test signals: The huge allocation expectation can be environment-sensitive on systems with aggressive overcommit. Invalid-data munmap error text is platform-specific. The tests do not verify stale byte clearing, concurrent access, or integration with `BlockPool`, but they do catch the main allocation lifecycle contract.
