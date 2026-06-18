# sources/user-network-fs/rclone/lib/mmap/mmap_test.go

Source read signal: reviewed complete local file (99 lines, sha256 9175f3dfe6112bfd).

Purpose: Tests and benchmarks memory-map allocation/free behavior.

Important APIs/types/functions: `TestAllocFree` and benchmarks for allocation/free across sizes and many allocations.

Control flow: The test allocates 4096 bytes, writes every byte, then frees. Benchmarks repeatedly allocate/free clean or dirtied pages and measure behavior with many pre-existing allocations.

State and persistence behavior: Allocates process memory only and frees it. Benchmarks can put pressure on virtual memory.

Dependencies and integration points: Uses `testing`, `fmt`, and `testify/assert`.

Risks and test signals: Basic correctness is covered, but double-free, derived-slice free, zero-size allocation, and allocation failure paths are not tested.
