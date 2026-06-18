# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/shm.c

Implements the illumos System V shared memory syscall module. It registers the `shmsys` syscall entry, exposes `shmat`, `shmctl`, `shmdt`, `shmget`, and `shmids`, and stores segment state in the generic IPC service layer.

Key responsibilities:
- Creates the `shmids` IPC service in `_init()` with project and zone resource controls for ID count and memory consumption.
- Enforces `zone.max-shm-ids`, `project.max-shm-ids`, `zone.max-shm-memory`, and `project.max-shm-memory`.
- Preserves obsolete `shminfo_*` tunables for compatibility.
- Maps shared memory through anonymous memory, `segvn`, and shared page table segments for ISM/DISM.
- Tracks per-process shared-memory mappings in `proc_t.p_segacct`, an AVL tree used by detach, fork, exit, and `/proc` lookup.

Important paths:
- `shmget()` creates or looks up a segment. New segments reserve anonymous memory with `anon_resv()`, allocate an `anon_map`, initialize IPC metadata, then commit through `ipc_commit_begin()` / `ipc_commit_end()`.
- `shmat()` validates permissions and flags, chooses normal `segvn_create` mapping or ISM/DISM `segspt_shmattach`, performs address alignment/range checks, maps into the process address space, and records a `segacct_t`.
- `shmdt()` removes the exact starting-address entry from `p_segacct`, unmaps the address range, updates detach accounting, and releases the IPC hold.
- `shmctl()` implements `IPC_SET`, `IPC_STAT`, 64-bit variants, `IPC_RMID`, `SHM_LOCK`, and `SHM_UNLOCK`.
- `shmfork()` duplicates parent segment-accounting records into a child and increments IPC references.
- `shmexit()` detaches all segments during process exit.
- `shmgetid()` supports `/proc` address-to-shmid lookup without taking `p_lock`.

Memory and locking model:
- IPC object locks come from `ipc_lookup()`, `ipc_get()`, and `ipc_lock()`.
- Address-space changes are protected by `as_rangelock()`.
- Anonymous map size/refcount/page state uses `ANON_LOCK_ENTER`.
- Per-process mapping records use `p_lock` plus `prbarrier()` to coordinate with `/proc`.
- Locked shared memory uses a temporary address space, `MC_LOCK`, page lookup, page lock counts, and locked-memory rctl accounting.

Filesystem relevance:
- This is VM/IPC rather than filesystem code, but it is directly relevant to the OS memory substrate used alongside VFS behavior. It exercises anon/swap objects, vnode-backed swap translation through `swap_xlate()`, and address-space segment operations that interact with page and vnode abstractions.

Notable edge cases:
- `share_page_table` and `ism_off` tunables rewrite attach flags.
- ISM/DISM attach mode cannot be changed once a shared page table segment exists.
- Segment size accounting uses rounded page size for resource controls but preserves the original requested byte size for user-visible `IPC_STAT`.
- `shm_dtor()` releases ISM resources, locked pages, anon reservations, and project/zone usage only after all references and `IPC_RMID` are gone.
