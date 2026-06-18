# sources/test-tools/ior/src/aiori-PMDK.c

## Purpose
Implements a low-level PMDK/libpmem backend for IOR using persistent-memory mapped files. It is restricted to file-per-process workloads.

## Important APIs, Types, and Functions
- `pmdk_aiori` registers PMDK create/open/xfer/close/delete/fsync/file-size callbacks and POSIX metadata helpers.
- `PMDK_Create` maps a new persistent-memory file with `pmem_map_file` using `PMEM_FILE_CREATE | PMEM_FILE_EXCL`.
- `PMDK_Open` maps an existing file with `pmem_map_file`.
- `PMDK_Xfer` writes with `pmem_memcpy_persist` or `pmem_memcpy_nodrain` depending on `fsyncPerWrite`, and reads with `memcpy`.
- `PMDK_Fsync` drains pending PMDK stores with `pmem_drain`.
- `PMDK_Delete` unlinks the backing file; `PMDK_GetFileSize` stats it.

## Control Flow
Create/open abort the MPI job if `hints->filePerProc` is false or if the mapped file is not detected as persistent memory. Transfer treats the `aiori_fd_t *` as the mapped address and applies byte offsets directly.

## State and Persistence
Persistent state is the pmem-backed file. Runtime state is global hints and mapped-address handles. Writes are persistent immediately with `pmem_memcpy_persist`, or require later drain when using no-drain per-write mode.

## Dependencies and Integration Points
Requires libpmem, MPI, IOR hints, and POSIX metadata helpers. `enable_mdtest = false`, reflecting that the backend is data-transfer oriented.

## Risks and Edge Cases
- `PMDK_Close` unmaps only `hints->transferSize`, while create/open map `blockSize * segmentCount`; that risks incomplete unmap.
- File-per-process restriction is enforced at runtime by MPI abort.
- `PMDK_Xfer` indexes `file[offset_size]` on `aiori_fd_t *`; correctness depends on this pointer being byte-addressable as returned from `pmem_map_file`.
- No dry-run handling.

## Test Signals
Run only on real or emulated pmem, validate file-per-process enforcement, mapping length/unmap correctness, persistence with and without `fsyncPerWrite`, file-size checks, and delete behavior.
