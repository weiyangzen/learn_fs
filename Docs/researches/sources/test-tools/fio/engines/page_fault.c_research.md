# sources/test-tools/fio/engines/page_fault.c

## Purpose
Implements a synchronous diskless engine that performs I/O against anonymous private memory. The goal is to benchmark or exercise page-fault behavior by reading/writing an mmap'd region rather than a real file.

## Important APIs, Types, And Functions
`struct fio_page_fault_data` stores the anonymous mapping pointer and size. Key functions are `fio_page_fault_init()`, `fio_page_fault_queue()`, `fio_page_fault_cleanup()`, and no-op open/close hooks.

## Control Flow
`init` rejects multiple files and nonzero `start_offset`, allocates state, maps `td->o.size` bytes with `MAP_PRIVATE | MAP_ANONYMOUS`, and stores it in `td->io_ops_data`. `queue` validates state and bounds, computes the mapped address from `io_u->offset`, copies from mapping on reads, copies to mapping on writes, treats sync directions as no-ops, and rejects unsupported directions. Cleanup unmaps and frees state.

## State And Persistence
All data is volatile anonymous memory and disappears at cleanup/process exit. There is no file persistence despite generic file-size integration.

## Dependencies And Integration Points
Depends on `mmap()`/`munmap()` and fio synchronous diskless engine hooks. Generic file-size callback is present, but open/close are no-ops.

## Risks
The mapping size is exactly `td->o.size`; any workload that generates offsets beyond that returns EINVAL. It does not support multiple files or start offsets. Mapping failure returns 1 without setting detailed fio error state.

## Test Signals
Test single-file read/write, sync no-op directions, unsupported directions, out-of-bounds offsets, multiple-file rejection, start-offset rejection, mapping allocation failure, and cleanup unmap.
