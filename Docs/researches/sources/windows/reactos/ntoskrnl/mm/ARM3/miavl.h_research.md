# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/miavl.h

## Role

`miavl.h` is the glue layer that adapts ReactOS/RTL AVL tree algorithms for ARM3 memory-manager VAD trees. It renames generic RTL AVL routines into `Mi*` symbols and supplies memory-manager-specific node accessors, comparison, parent/balance packing, and child insertion helpers.

## Key mechanisms

- Aliases `PRTL_AVL_TABLE` to `PMM_AVL_TABLE` and `PRTL_BALANCED_LINKS` to `PMMADDRESS_NODE`, allowing generic AVL code to compile against MM VAD structures.
- Renames core AVL routines (`RtlpFindAvlTableNodeOrParent`, promotion, rebalancing, insert, delete) to `Mi*` names to avoid symbol conflicts if not inlined.
- Provides `MiAvlCompareRoutine`, which treats the lookup buffer as a `StartingVpn` and compares it against a node's inclusive `[StartingVpn, EndingVpn]` range. This is the core VAD containment comparison.
- Handles the MM-specific packed parent/balance representation. `MiSetParent` preserves the low two balance bits when replacing the parent pointer; `MiParentAvl` masks those bits off when retrieving the parent.
- Exposes child/relationship helpers (`MiRightChildAvl`, `MiLeftChildAvl`, `MiIsLeftChildAvl`, `MiIsRightChildAvl`) and insertion helpers that set parent links as they attach nodes.

## Dependencies and coupling

- Requires the `MMADDRESS_NODE` layout where `u1.Parent` and `u1.Balance` share storage and where `StartingVpn`/`EndingVpn` live inline in the node.
- Intended to be included before or with the generic AVL implementation so macro renames affect the compiled symbols.
- Used by VAD tree operations declared in `miarm.h`, including lookup, conflict detection, empty-range search, insertion, and removal.

## Research notes

- The low-bit parent packing assumes parent pointers are at least 4-byte aligned; the header comments say at least 8-byte aligned, which is sufficient for the two low balance bits.
- The compare routine returns equality for any VPN inside the node range, not just exact start matches, which is why it is appropriate for VAD interval lookup.
