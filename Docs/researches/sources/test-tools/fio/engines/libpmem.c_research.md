# sources/test-tools/fio/engines/libpmem.c

## Purpose
Implements a PMDK libpmem-backed synchronous engine. It maps files from a DAX-capable persistent-memory filesystem with `pmem_map_file()`, reads with `memcpy()`, writes with `pmem_memcpy()`, and drains persistence on sync operations or synchronous write settings.

## Important APIs, Types, And Functions
`struct fio_libpmem_data` stores the mapped pointer, mapped size, and map offset for each fio file. Key functions are `fio_libpmem_init()`, `fio_libpmem_file()`, `fio_libpmem_open_file()`, `fio_libpmem_prep()`, `fio_libpmem_queue()`, and `fio_libpmem_close_file()`.

## Control Flow
`init` rejects block sizes smaller than a page when fsync/fdatasync options require mmap-style page granularity. `open_file` allocates per-file data, sets map size to `f->io_size`, and calls `pmem_map_file()` with create permissions. `prep` validates the block size does not exceed real file size and points `io_u->mmap_data` at the mapped address plus fio offset. `queue` copies from mapped memory for reads, copies to mapped memory for writes using flags derived from `sync_io` and `odirect`, and calls `pmem_drain()` for sync-like directions.

## State And Persistence
The persistent backing is the mapped file on a DAX filesystem. Per-file engine data tracks one mapping. `sync=1` or explicit sync operations ensure `pmem_drain()`; otherwise writes use `PMEM_F_MEM_NODRAIN` and may require later drain.

## Dependencies And Integration Points
Depends on PMDK `libpmem`, fio verify support, file prepopulation, generic size handling, and fio `FIO_MEMALIGN`/`FIO_BARRIER` behavior. It is synchronous and diskless from fio's perspective.

## Risks
`pmem_map_file()` can succeed on non-pmem files; the code reports an error but retains mapping until error cleanup. Close uses `ret &= generic_close_file()`, which can mask return semantics. It assumes mapping size is `f->io_size` and does not implement remapping for offsets beyond that. Pointer arithmetic on `void *` is a compiler extension.

## Test Signals
Test DAX and non-DAX paths, read/write/sync with `sync=0` and `sync=1`, `direct=1` nontemporal mode, too-small block sizes with fsync/fdatasync, oversized block rejection, verify workloads, map/unmap failure handling, and prepopulation integration.
