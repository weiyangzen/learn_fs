# File Research: sources/os/bsd/dragonflybsd/sys/kern/sysv_shm.c

## Summary
Implements SVID/System V shared memory. It manages shared-memory segment descriptors, VM objects, per-vmspace attachment maps, attach/detach/control/get syscalls, fork/exit inheritance, and shared-memory tunables.

## Main Responsibilities
- Initializes shared-memory limits and descriptor table in `shminit()`.
- Finds segments by key or shmid with sequence validation and optional removed-segment attachment support.
- Allocates segments in `shmget_allocate_segment()` using physical or swap pager VM objects.
- Handles keyed lookup and creation in `sys_shmget()`.
- Maps segments into process address spaces in `sys_shmat()`.
- Detaches mappings in `sys_shmdt()` and `shm_delete_mapping()`.
- Handles `IPC_STAT`, `IPC_SET`, and `IPC_RMID` in `sys_shmctl()`.
- Copies attachment state across fork in `shmfork()` and detaches all segments on vmspace exit in `shmexit()`.
- Deallocates segment VM objects when removed and no longer attached.

## Important Behavior
Global state is serialized by `shm_token`. Each process vmspace lazily receives a `vm_shm` array of `struct shmmap_state`, capped by `shminfo.shmseg`. Attach reserves an entry before VM operations because blocking may temporarily lose serialization.

`shmget_allocate_segment()` marks a descriptor as allocated-but-removed while allocating memory so competing keyed creators wait instead of creating a duplicate. After pager object creation it installs owner/mode metadata, accounts committed pages, and wakes waiters if needed. `shm_use_phys` selects physical pager allocation by default; values above 1 trigger eager page preallocation up to available free pages.

`sys_shmat()` supports fixed addresses, `SHM_RND`, read-only protection, inherited shared mappings, and segment-size alignment to `SEG_SIZE` for large mappings when possible. `IPC_RMID` marks a segment removed and deallocates it only after the attachment count reaches zero. `shm_allow_removed` permits attaching to removed-but-still-referenced segments by shmid.

## Dependencies and Integration
This file depends on `ipcperm()`, jail SysV IPC capability checks, VM maps, VM objects, physical/swap pagers, pmap/page APIs, process vmspaces, sysctl/tunables, and SysV IPC ID macros.

## Risks
Attachment bookkeeping and VM map removal must stay synchronized with `shm_nattch`; failed or racing detach paths can leak mappings or deallocate too early. `shmfork()` assumes the parent vmspace has a valid `vm_shm` array when invoked. Eager physical-page preallocation can stall the kernel for large segments, which the comments acknowledge.
