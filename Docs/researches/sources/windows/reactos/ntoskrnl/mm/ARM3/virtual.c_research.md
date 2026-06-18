# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/virtual.c

## Role In Subset

Implements ReactOS ARM3 virtual memory management and the user-facing NT virtual-memory syscalls. This is a central bridge between VAD address-space metadata, page-table/PTE manipulation, PFN accounting, working-set locking, process attach/detach, and user probe/SEH behavior.

## Main Responsibilities

- Counts committed pages over VAD ranges with `MiCalculatePageCommitment`, including multi-level page-table gaps and decommitted PTE detection.
- Ensures page-table pages are resident through `MiMakeSystemAddressValid`, `MiMakeSystemAddressValidPfn`, and `MiMakePdeExistAndMakeValid`.
- Deletes mapped virtual ranges via `MiDeletePte`, `MiDeleteVirtualAddresses`, and `MiDeleteSystemPageableVm`, updating PFN share/reference counts and page-table references.
- Copies memory between processes with `MmCopyVirtualMemory`, selecting MDL-backed mapped copy for larger transfers and pool/stack copy for smaller transfers.
- Implements `NtReadVirtualMemory`, `NtWriteVirtualMemory`, `NtProtectVirtualMemory`, `NtAllocateVirtualMemory`, `NtFreeVirtualMemory`, `NtQueryVirtualMemory`, lock/unlock VM calls, instruction-cache flush, and physical-address lookup.
- Supports private demand-zero allocation, commit, decommit, release, VAD splitting, and basic section commit paths for ARM3 sections.
- Queries memory state/protection by combining VAD metadata, page-table state, prototype PTEs, PFN `OriginalPte`, and special shared-user-data handling.

## Important Internal Flows

- `NtAllocateVirtualMemory` validates flags, probes user outputs, references/attaches to the target process, creates VADs for reserve/blind commit, or commits into an existing VAD by writing demand-zero PTEs and updating commit accounting.
- `NtFreeVirtualMemory` handles `MEM_RELEASE` and `MEM_DECOMMIT`; release can remove an entire VAD, trim from front/back, or split a VAD in the middle before deleting PTEs.
- `MiProtectVirtualMemory` validates VAD range and protection, rejects unsupported VAD types, confirms private ranges are fully committed, then updates valid or invalid PTE protections.
- `MiDecommitPages` batches valid PTE teardown in `MiProcessValidPteList` to reduce repeated TLB flushes.
- `MiLockVirtualMemory` probes every page, faults missing pages in, then marks PFN-embedded WSLE lock bits; `MiUnlockVirtualMemory` validates all requested locks before dropping them.

## Locking And State Assumptions

- VAD operations use process address-space locks.
- PTE/PFN deletion paths require PFN lock and exclusive working-set ownership.
- Query/protection paths frequently assume current-process attachment when touching user page tables.
- Page-table page residency helpers intentionally release/reacquire working-set or PFN locks while faulting kernel page-table addresses back in.
- Several paths assert no clone/fork support and no unsupported prototype/shared-page combinations.

## Notable Limitations

- `MmFlushVirtualMemory` is unimplemented but returns `STATUS_SUCCESS` while reporting `STATUS_NOT_IMPLEMENTED` in the I/O status block.
- `MmGetVirtualForPhysical`, `MmSecureVirtualMemory`, and `MmUnsecureVirtualMemory` are placeholders.
- `NtGetWriteWatch` and `NtResetWriteWatch` are unimplemented but return success-like results after validation.
- Large pages, physical memory VADs, write-watch allocation, many section protection changes, file-backed ARM3 section assumptions, fork/clone, and several prototype-PTE scenarios are unsupported or assertion-only.
- SMP TLB invalidation is incomplete in protection changes involving transition PTEs.
- `MEM_RESET` currently pretends success without doing reset semantics.

## Filesystem-Relevant Notes

Virtual-memory behavior here affects mapped files, section views, cache interaction, paging I/O, and user/kernel buffer copying used by filesystem paths. The section-related code is partial: private memory is the strongest path, while file-backed mapped section behavior has explicit unsupported assertions and delegation to legacy section-view helpers in query/protect cases.
