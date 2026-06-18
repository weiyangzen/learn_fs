# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/miarm.h

## Role

`miarm.h` is the central private header for the ReactOS ARM3 memory manager. It defines architecture-sensitive page table protection constants, memory-manager policy constants, internal MM/session/pool/PFN data structures, global state declarations, inline helpers, and cross-file prototypes used by ARM3 initialization, paging, VAD, section, pool, and PFN code. Despite the name, it is not ARM-only; it carries conditionals for x86, AMD64, and ARM.

## Key mechanisms

- Defines internal MM protection values (`MM_READONLY`, `MM_READWRITE`, guard/noaccess/decommit encodings) and maps them to architecture-specific PTE bits for x86, AMD64, and ARM. The PTE bit section distinguishes access flags, valid/accessed/dirty bits, cache-disable/write-combine bits, prototype bits, and a per-architecture `PTE_PROTECT_MASK`.
- Provides address classification macros for session space, session images, session PTEs, page-table ranges, system page-table ranges, and page-table/hyperspace ranges. These are used as cheap assertions and policy checks around PTE manipulation.
- Defines ReactOS/NT-style pool metadata (`POOL_DESCRIPTOR`, `POOL_HEADER`, pool tracker tables, big-page trackers) pending a pool merge into executive headers. The definitions encode 32-bit vs 64-bit layout differences and assert header size/alignment.
- Defines session structures (`MMSESSION`, `MM_SESSION_SPACE_FLAGS`, `MM_SESSION_SPACE`) covering session views, session paged pool, session working set support, image lists, Win32K unload hook, and architecture-specific page-table storage.
- Declares nearly all ARM3 global variables: canonical PTE/PDE templates, pool boundaries, session-space boundaries, physical-memory descriptors, PFN coloring data, working-set state, memory threshold events, system cache state, PFN database metadata, process list, zeroing event, expansion lock state, and section/VAD roots.
- Implements inline PTE constructors: `MI_MAKE_HARDWARE_PTE_KERNEL`, `MI_MAKE_HARDWARE_PTE`, `MI_MAKE_HARDWARE_PTE_USER`, `MI_MAKE_TRANSITION_PTE`, and for non-AMD64 builds, prototype/subsection PTE encoders. The user/global owner selection is centralized in `MiDetermineUserGlobalPteMask`.
- Implements low-level PTE/PDE write helpers (`MI_WRITE_VALID_PTE`, `MI_UPDATE_VALID_PTE`, `MI_WRITE_INVALID_PTE`, `MI_ERASE_PTE`, `MI_WRITE_VALID_PDE`, `MI_WRITE_INVALID_PDE`) with assertions that enforce valid/invalid state transitions and page-frame consistency.
- Implements working-set lock helpers for process, system cache, and session working sets. The helpers track ownership on `ETHREAD`, enter/leave guarded regions for safe acquisitions, support shared/exclusive variants, handle unsafe fault-time acquisitions, and provide conversion from shared to exclusive.
- Implements PFN lock-count/reference helpers used by MDL probing and locked-page accounting: `MiDropLockCount`, `MiDereferencePfnAndDropLockCount`, `MiReferenceProbedPageAndBumpLockCount`, `MiReferenceUsedPageAndBumpLockCount`, and `MiReferenceUnusedPageAndBumpLockCount`.
- Declares the main initialization and subsystem entry points: `MmArmInitSystem`, session-space layout/init, machine-dependent init, PFN database mapping/initialization, color tables, memory events, system PTE reserve/release, MDL page allocation, PFN list manipulation, VAD lookup/insertion/removal, section view unmapping, address validation, pageable VM deletion, system image write-protection, and PDE deletion.
- Provides page-table reference accounting for two-level builds through `MmWorkingSetList->UsedPageTableEntries`, and for three/four-level builds through PFN `OriginalPte.u.Soft.UsedPageTableEntries`. `MiDeletePde` cascades deletion up the paging hierarchy when reference counts hit zero.

## Dependencies and coupling

- Depends on kernel-wide ReactOS NT structures and macros from `ntoskrnl.h`, including `MMPTE`, `MMPDE`, `MMPFN`, `MMSUPPORT`, `EPROCESS`, `ETHREAD`, page-table address macros, PFN database accessors, push locks, guarded regions, and cache/PTE manipulation macros.
- Serves as the shared private contract for the ARM3 files in this directory. Many `.c` files include it after defining `MODULE_INVOLVED_IN_ARM3`.
- The header is tightly coupled to Windows NT memory-manager layout assumptions: session-space virtual layout, paged/nonpaged pool boundaries, system PTE pools, PFN database representation, VAD AVL tables, and prototype/subsection PTE packing.
- Several areas are explicitly transitional or incomplete, including comments such as `FIXFIX` around pool definitions and commit accounting warnings for prototype PTE lock-count changes.

## Research notes

- This file is high-value architectural glue rather than a standalone implementation. When following behavior in other ARM3 files, most invariants around PTE construction, working-set ownership, and PFN reference accounting are defined here.
- The inline assertions are part of the design: they document assumptions about caller lock ownership, valid page-table state, non-session vs session mappings, and page-frame identity.
- The file includes architecture-sensitive branches; any research using it should note target architecture because prototype PTE encoding, page-table reference accounting, and user PTE/PDE detection differ by paging level.
