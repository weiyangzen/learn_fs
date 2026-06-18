# sources/test-tools/fio/os/windows/posix/include/sys/shm.h

Purpose: declares a limited System V shared-memory facade for Windows.

Important APIs/types: defines `IPC_RMID`, `IPC_CREAT`, `IPC_PRIVATE`; typedefs `uid_t`, `gid_t`, `shmatt_t`, and `key_t`; declares `ipc_perm`, `shmid_ds`, and `shmget()`/`shmat()`/`shmdt()`/`shmctl()`.

Control flow and state: `posix.c` backs `shmget()` with pagefile-backed `CreateFileMapping()`, stores handles in a fixed global array, maps them with `MapViewOfFile()`, commits pages with `VirtualAlloc()`, and unmaps with `UnmapViewOfFile()`.

Dependencies and integration: used by fio code expecting process-shared memory on Unix-like systems while building on Windows.

Risks: permissions, keys, attach counts, ownership, and most `shmctl()` commands are not implemented. The fixed handle table has no bounds checks, no synchronization, and no true key reuse semantics.

Test signals: Windows shared-memory allocation/attach/detach lifecycle tests and stress tests around many segments.
