# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/procsup.c

This file implements ARM3 process-related memory management: PEB/TEB VAD creation and deletion, kernel stack allocation/growth/freeing, memory-priority setting, PEB/TEB initialization, process address-space initialization/cleanup/deletion, hand-built process setup, and unimplemented AWE-style user physical page syscalls.

Core globals:
- `MmProcessColorSeed` seeds per-process page-color selection.
- `MmMaximumDeadKernelStacks` and `MmDeadStackSListHead` implement a small cache of dead non-GUI kernel stacks.
- `MmRotatingUniprocessorNumber` rotates affinity for uniprocessor-only images.

PEB and TEB support:
- `MiCreatePebOrTeb` allocates an `MMVAD_LONG`, charges nonpaged quota, initializes a private committed read-write no-change VAD, and inserts it top-down. PEB placement adds a small randomized offset near the highest VAD address.
- `MmCreatePeb` attaches to the target process, maps NLS data, creates the PEB VAD, initializes PEB fields, reads image headers/config under SEH, applies version, CSD, affinity, subsystem, and debugging fields, then returns the PEB address.
- `MmCreateTeb` attaches to the target process, creates the TEB VAD, initializes TIB/TEB identity, stack bounds, client IDs, locale, PEB pointer, and static Unicode string.
- `MmDeleteTeb` attaches to the process, locks address creation and working set, removes the TEB VAD, deletes the virtual address range, frees the VAD, and returns VAD quota.

Kernel stack support:
- `MmCreateKernelStack` reserves system PTEs plus a guard page, allocates and maps committed stack pages, initializes PFNs, and returns the top of stack. GUI stacks reserve a larger range but initially commit only `KERNEL_LARGE_STACK_COMMIT`.
- Non-GUI stacks can be reused from `MmDeadStackSListHead`.
- `MmDeleteKernelStack` pushes small non-GUI stacks to the dead-stack S-list when possible; otherwise it walks stack PTEs, marks PFNs deleted, decrements page-table and page share counts, and releases system PTEs.
- `MmGrowKernelStackEx` validates growth against reserved stack space, allocates pages down to the requested new limit, writes valid stack PTEs, and updates `Thread->StackLimit`.
- `MmGrowKernelStack` calls the extended version with the large-stack commit size.

Process address-space creation:
- `MmCreateProcessAddressSpace` allocates zeroed pages for the process directory table, hyperspace, and working-set list, records them in `DirectoryTableBase` and `WorkingSetPage`, calls architecture-specific setup, moves initialization to phase 1, and adds the process to session tracking.
- `MmInitializeProcessAddressSpace` attaches to the process, initializes locks and VAD root, initializes PFNs for the process page-directory/hyperspace/working-set pages, initializes the working-set list, records the owning process in the page-directory PFN, optionally inserts an AMD64 shared-user-page VAD, maps the executable section, stores image name/audit name, and completes phase 2.
- `MmInitializeHandBuiltProcess` shares directory bases and working-set data with the idle/current process for bootstrapped processes.
- `MmInitializeHandBuiltProcess2` is a placeholder that currently returns success.

Cleanup and deletion:
- `MmCleanProcessAddressSpace` removes the process from its session, skips incomplete address spaces with a warning, marks VM deleted, walks all VADs, delegates legacy ReactOS memory areas to RosMm, removes ARM3 VADs, unmaps section views or deletes private ranges, frees VADs, returns quota, deletes shared user data, and unlocks the address space.
- `MmDeleteProcessAddressSpace` removes the process from memory-manager lists, deletes working-set, hyperspace, and directory-table PFNs for fully initialized processes, releases session references, and clears directory table bases.
- Partially initialized address spaces are warned as possible leaks.

Other APIs:
- `MmSetMemoryPriorityProcess` stores process memory priority, forcing background priority on very small systems.
- `MiInsertSharedUserPageVad` exists only for AMD64 and inserts a read-only VAD for `MM_SHARED_USER_DATA_VA`.
- `NtAllocateUserPhysicalPages`, `NtMapUserPhysicalPages`, `NtMapUserPhysicalPagesScatter`, and `NtFreeUserPhysicalPages` are explicit `UNIMPLEMENTED` stubs returning `STATUS_NOT_IMPLEMENTED`.

Notable limitations and risk points:
- Cleanup has explicit legacy interop with RosMm VADs, so address-space teardown depends on mixed ARM3/RosMm ownership checks.
- Partially initialized address spaces may leak resources by design.
- Stack caching avoids freeing small non-GUI stacks until the dead-stack cache fills.
- `MmCreatePeb` and `MmCreateTeb` may return after SEH failures without fully undoing all earlier allocations or mappings in every branch.
- AWE/user physical pages are not implemented.
- Several process initialization routines depend on architecture-specific page-table layout and `MiArchCreateProcessAddressSpace`.
