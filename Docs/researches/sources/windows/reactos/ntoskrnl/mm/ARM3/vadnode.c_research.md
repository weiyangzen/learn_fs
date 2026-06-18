# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/vadnode.c

ReactOS ARM3 virtual address descriptor node algorithms built on the memory-manager AVL table support.

Key responsibilities:
- Defines `MmReadWrite`, a protection-mask permission table used for secured VAD checks.
- Imports AVL support through `miavl.h` and `sdk/lib/rtl/avlsupp.c`.
- Provides debug-only lock assertions for process VAD trees, the ReactOS kernel VAD root, and the section-based root.
- Locates VADs by address with `MiLocateVad()` and `MiLocateAddress()`, using `NodeHint` before falling back to AVL search.
- Detects overlap and insertion position with `MiCheckForConflictingNode()`.
- Inserts process VADs and generic address nodes with `MiInsertNode()`, `MiInsertVad()`, and `MiInsertVadEx()`.
- Inserts based sections into `MmSectionBasedRoot` with `MiInsertBasedSection()`.
- Removes nodes with `MiRemoveNode()` and maintains `NodeHint`.
- Walks predecessor/successor links with `MiGetPreviousNode()` and `MiGetNextNode()`.
- Finds free address ranges bottom-up, top-down, and in the section-based tree with `MiFindEmptyAddressRangeInTree()`, `MiFindEmptyAddressRangeDownTree()`, and `MiFindEmptyAddressRangeDownBasedTree()`.
- Enforces secured/no-change VAD rules with `MiCheckSecuredVad()`.

Important behavior:
- Process VAD writes require both the process working-set lock and `AddressCreationLock` in debug builds; kernel VAD writes require system working-set exclusivity and the idle process address creation lock.
- `MiInsertVadEx()` aligns the requested view size, acquires the current process address creation lock, rejects terminating processes, chooses an address by caller-specified base or top-down/bottom-up search, computes VPN bounds, sets commit charge for committed private memory or write-copy mapped memory, handles one-secured long VAD metadata, inserts under the working-set lock, and updates process virtual-size counters.
- Bottom-up range search starts from the lowest relevant user or kernel VPN and walks in-order until it finds a gap.
- Top-down range search starts below a boundary address, walks backward through predecessor nodes, and returns the highest aligned fitting gap.
- Section-based top-down search returns `STATUS_SUCCESS`/`STATUS_NO_MEMORY` instead of AVL insertion results and carries a compatibility branch for pre-Vista behavior.
- `MiCheckSecuredVad()` blocks protection changes that violate `NoChange`/`SecNoChange`, denies decommit-style changes against the secured subrange, and requires read-write-compatible protections for one-secured VAD ranges.

Dependencies:
- Depends on `MM_AVL_TABLE`, `MMADDRESS_NODE`, `MMVAD`, `MMVAD_LONG`, `EPROCESS`, working-set lock state, guarded mutex ownership, and ARM3 address constants.
- Uses RTL AVL primitives: `RtlpFindAvlTableNodeOrParent()`, `RtlpInsertAvlTreeNode()`, `RtlpDeleteAvlTreeNode()`, `RtlLeftChildAvl()`, `RtlRightChildAvl()`, `RtlParentAvl()`, and child-side predicates.
- Uses process globals and locks: `PsGetCurrentProcess()`, `PsGetCurrentThread()`, `PsIdleProcess`, `MiRosKernelVadRoot`, `MmSectionBasedRoot`, and `MmSectionBasedMutex`.

Notable risks:
- Lock enforcement is debug-only; release builds rely on callers honoring the locking contract.
- Several range routines use names like `LowVpn` while switching between byte addresses and VPN/page counts, so alignment/unit correctness is subtle.
- `MiInsertVad()` assumes the caller already proved no conflict; it asserts rather than returning a conflict status.
- `MiCheckSecuredVad()` asserts that multiple secured regions and read-only secured VADs are unsupported.
- Kernel-mode address search is keyed off `Table->Unused == 1`, an implicit table-mode convention that must be preserved by callers.
