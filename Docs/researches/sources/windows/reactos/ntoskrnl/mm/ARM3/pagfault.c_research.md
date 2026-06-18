# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/pagfault.c

This file implements ARM3 page-fault handling for ReactOS, including user/kernel fault routing, demand-zero faults, transition faults, pagefile faults, prototype PTE faults, copy-on-write, guard-page stack growth, session/paged-pool PDE fixups, and process execute-option APIs.

Core responsibilities:
- `MmArmAccessFault` is the top-level fault handler. It separates high-IRQL faults, kernel faults, page-table/hyperspace faults, and user faults.
- `MiDispatchFault` handles the lower-level PTE state machine after locks and address validity have been established.
- `MiResolveDemandZeroFault`, `MiResolveTransitionFault`, `MiResolvePageFileFault`, and `MiResolveProtoPteFault` implement the major invalid-PTE recovery paths.
- `MiAccessCheck` and `MiIsAccessAllowed` enforce software protection bits before resolving user faults.
- `MiCheckVirtualAddress` maps a virtual address to VAD/protection/prototype-PTE information.
- `MiCheckForUserStackOverflow` consumes guard-page faults to extend user stacks or report stack overflow.
- `MmGetExecuteOptions` and `MmSetExecuteOptions` expose process NX/execute policy flags.

Major control flow:
- High-IRQL faults are only allowed when all required paging structures are already valid. Invalid entries lead to an in-page-style failure or bugcheck diagnostics.
- Kernel faults reject user-mode access to kernel addresses, validate upper paging levels, handle paged-pool/session PDE fixups on 2-level paging, then take the system or session working-set lock and dispatch.
- User faults take the process working-set lock, allocate missing PXE/PPE/PDE page-table pages as demand-zero pages, then handle valid PTE write/COW/NX cases or invalid PTE resolution.
- Empty user PTEs are checked against the VAD tree. If committed private memory, the code creates a software PTE and allocates a zeroed physical page. If section-backed, it creates or follows a prototype PTE.
- Guard pages are converted to non-guard protection and delegated to stack-overflow/stack-extension handling after dropping the working-set lock.

Important data and invariants:
- `HYDRA_PROCESS` is a sentinel process pointer for session-backed faults.
- `UserPdeFault` is only present when PFN tracing is enabled and annotates page-table demand-zero allocation.
- Fault paths assume APCs are disabled and IRQL is at most APC_LEVEL except the special high-IRQL case.
- PFN-lock ownership is central. Some helpers release the PFN lock internally, especially prototype-fault completion.
- Hardware PTE construction is split between user and kernel mappings through `MI_MAKE_HARDWARE_PTE_USER` and `MI_MAKE_HARDWARE_PTE`.

Demand-zero behavior:
- `MiResolveDemandZeroFault` chooses zeroed, free, or any colored page depending on process context, session image/view addresses, and whether the caller already owns the PFN lock.
- It initializes the PFN, updates demand-zero counters, optionally zeroes the page outside the lock, writes a valid PTE, and increments `NumberOfPrivatePages` for real processes.
- User PDE faults are treated as kernel PTE mappings for page tables.

Prototype and transition behavior:
- `MiCompleteProtoPteFault` converts a valid prototype PTE into a process PTE, updates PFN share counts, applies protection/caching, and releases the PFN lock.
- `MiResolveProtoPteFault` handles valid proto PTEs, reserved section access, COW on write-copy mappings, transition prototype PTEs, and demand-zero prototype backing.
- COW creates a private page with `MiCopyPfn`, deletes the old PTE reference, initializes the new PFN, converts write-copy to read-write, and writes a private valid PTE.
- Transition faults remove standby/free pages from lists, bump references/share counts, restore active-valid state, and may wait on in-progress read/write events.

Pagefile behavior:
- `MiResolvePageFileFault` allocates a replacement page, marks it read-in-progress, writes a transition PTE before dropping the PFN lock, reads from the pagefile, reacquires the lock, then makes the PTE valid and wakes waiters.
- The path asserts a real process context and a held PFN lock, and treats failed paging I/O as an assertion/in-page error path.

Notable limitations and risk points:
- Many Windows-compatible cases are explicitly asserted rather than implemented: AWE VADs, physical-memory VADs, image VADs in some paths, clone PTEs, mapped-file paged-out prototype PTEs, large pages, and some session-space paths.
- Session-space support is incomplete outside the 2-level paging implementation, with an explicit warning.
- Double transition faults are not supported.
- Clustered prototype faults are stubbed to a single PTE.
- Stack guarantee support is asserted to zero, so guaranteed stack bytes are not implemented.
- `MiAccessCheck` ignores the `Execute` argument in callers except through the local helper, and most fault execute checks happen later on valid PTEs.
- Many failure modes are debug assertions or bugchecks rather than recoverable statuses, reflecting ARM3 incompleteness in this ReactOS snapshot.
