# sources/test-tools/strace/src/ipc_shm.c

Purpose: decodes SysV shared-memory creation, attach, and detach syscalls.

Important APIs/types/functions: `SYS_FUNC(shmget)`, `SYS_FUNC(shmat)`, `SYS_FUNC(shmdt)`, `print_shmaddr_shmflg`, `SHM_HUGE_SHIFT`, `SHM_HUGE_MASK`, and xlats `shm_resource_flags`/`shm_flags`.

Control flow: `shmget` prints key, size, and flags, specially splitting hugetlb page-size bits from resource flags before printing permission mode bits. `shmat` prints input arguments on entry and on successful exit returns the attached address as hex, reading the indirect return address slot for legacy IPC. `shmdt` prints the address from direct or indirect argument positions.

State and persistence behavior: no persistent state. `shmat` mutates `tcp->u_rval` on indirect successful exits to reflect the real attached address read from tracee memory.

Dependencies and integration points: uses IPC provider selection, shared-memory flag xlat tables, indirect IPC detection, and return-value formatting flags.

Risks: hugepage flag decoding must keep masks in sync with kernel constants. Indirect `shmat` can fail to read the returned address and then suppresses normal return formatting.

Test signals: cover normal and hugetlb `shmget` flags, direct/indirect `shmat`, failed attach, unreadable indirect return slot, `SHM_RDONLY`/`SHM_REMAP`, and `shmdt` argument mapping.
