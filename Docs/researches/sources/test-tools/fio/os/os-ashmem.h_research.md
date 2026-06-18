# sources/test-tools/fio/os/os-ashmem.h

## Purpose
`os-ashmem.h` emulates SysV shared-memory calls on Android/Bionic using ashmem or `ASharedMemory_create()` when normal SysV shared memory is unavailable.

## Important APIs, Types, and Functions
It maps `shmid_ds` to `shmid64_ds`, defines `SHM_HUGETLB`, and provides inline replacements for `shmctl()`, `shmget()`, `shmat()`, and `shmdt()`. It uses `/dev/ashmem` unless `CONFIG_ASHAREDMEMORY_CREATE` enables the Android shared-memory API.

## Control Flow
`shmget()` creates or opens an ashmem object, names it from the key, and allocates requested size plus eight bytes for length storage. `shmat()` maps the full ashmem fd, stores the mapping size at the front, and returns an aligned pointer after that header. `shmdt()` subtracts one `uint64_t` to recover the stored size and unmaps. `shmctl(IPC_RMID)` unpins and closes the fd.

## State and Persistence
The only state is the fd-backed ashmem region and the hidden length word at the beginning of each mapping. Lifetime is fd/mapping scoped; there is no SysV-style global key registry in this shim.

## Dependencies and Integration Points
Android builds include this from `os-linux.h` under `__ANDROID__`. It integrates with fio's shared-memory allocation paths when `CONFIG_NO_SHM` is not set.

## Risks and Edge Cases
The shim only implements the subset fio needs. `shmat()` does not check `mmap()` failure before writing the length word, which is a risk if mapping fails. Key semantics and permission flags do not fully match SysV shared memory. `shmctl()` only meaningfully handles `IPC_RMID`.

## Test Signals
Android shared-memory allocation/free tests, failure injection for ashmem open/ioctl/mmap, alignment checks on 32-bit ARM, and fio shared-memory buffer runs are the key signals.
