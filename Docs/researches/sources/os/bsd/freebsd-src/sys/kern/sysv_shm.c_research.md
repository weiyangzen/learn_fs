# File Research: sources/os/bsd/freebsd-src/sys/kern/sysv_shm.c

## Purpose
Implements FreeBSD System V shared memory support as the `sysvshm` module, covering `shmget`, `shmat`, `shmdt`, `shmctl`, VM object backing, process fork/exit mapping hooks, jail scoping, accounting, sysctl export, Linux ABI info commands, and compatibility shims.

## Main Structures and State
- `struct shmid_kernel *shmsegs`: segment table.
- `struct shmmap_state`: per-process mapping record containing attach VA and shmid.
- Global counters: `shm_last_free`, `shm_nused`, `shmalloced`, `shm_committed`.
- `shminfo`: tunable limits for max/min size, number of IDs, segments per process, and total pages.
- `sysvshmsx`: exclusive `sx` lock protecting segment table and per-process SysV shm mapping state.

## Core Behavior
- `shminit()` initializes tunables, allocates segment table, installs fork/exit/object-info hooks when modular, configures jail OSD state, and registers syscalls.
- `sys_shmget()` finds a segment by key in the caller prison or allocates a new one.
- `shmget_allocate_segment()` enforces size/count/page limits, RACCT limits, allocates a swap- or phys-backed VM object, marks it `OBJ_SYSVSHM`, fills permissions/metadata, and returns an IPC id.
- `kern_shmat_locked()` validates ID/permission/MAC policy, allocates the process `vm_shm` array if needed, chooses/validates attach VA, maps the VM object with `vm_map_find()`, records attachment state, and increments `shm_nattch`.
- `kern_shmdt_locked()` finds a process mapping by VA and removes it with `vm_map_remove()`.
- `shm_delete_mapping()` decrements attach count, updates detach time, and deallocates removed segments after the last detach.
- `kern_shmctl_locked()` implements `IPC_STAT`, `IPC_SET`, `IPC_RMID`, plus Linux-facing `IPC_INFO`, `SHM_INFO`, and `SHM_STAT`.
- `shmfork_*()` duplicates the process mapping table and increments attach counts.
- `shmexit_*()` detaches all mappings during vmspace exit.

## Jail and Visibility Model
- `shm_find_prison()` maps a caller to the jail root for SysV shm.
- `shm_find_segment()` validates allocation, removal visibility, sequence number, and prison visibility.
- `shm_prison_*()` mirrors the semaphore jail model with `sysvshm` new/inherit/disable settings and cleanup of segments owned by a jail.

## External Interfaces
- Syscalls: `shmat`, `shmdt`, `shmget`, `shmctl`, old `shmsys` on supported compatibility builds.
- Sysctls under `kern.ipc.*`: `shmmax`, `shmmin`, `shmmni`, `shmseg`, `shmall`, `shm_use_phys`, `shm_allow_removed`, and `shmsegs`.
- `kern_get_shmsegs()` returns sanitized segment metadata.
- FreeBSD32 and old-FreeBSD compatibility paths translate structure layouts and saturate fields where necessary.

## Dependencies
Uses VM object/pager/map APIs, resource limits, RACCT, audit, MAC, jail OSD, syscall helper registration, sysctl, credentials, and process/vmspace lifecycle hooks.

## Notes and Risks
- The implementation serializes most operations through one `sx` lock, simplifying correctness but limiting concurrency.
- Segment removal is two-phase: `IPC_RMID` marks removed, and actual deallocation waits for `shm_nattch == 0`.
- `shm_allow_removed` controls whether removed-but-attached segments remain attachable.
