# File Research: sources/virtualization/qemu/block/qed-check.c

Implements QED image consistency checking and optional repair. It builds a bitmap of referenced clusters, walks the L1 table and every reachable L2 table, validates table/data cluster offsets, detects duplicate references as corruptions, and records allocation/fragmentation statistics in `BdrvCheckResult`.

`qed_check_l1_table()` marks the L1 table clusters, validates L2 table offsets, reads each L2 table, delegates data-cluster validation to `qed_check_l2_table()`, and writes repaired L1/L2 entries when `fix` is true. Invalid offsets are cleared to unallocated entries during repair. `qed_check_for_leaks()` scans file clusters after the header for unreferenced clusters, but only after a complete successful metadata walk.

`qed_check_mark_clean()` clears `QED_F_NEED_CHECK` only if there are no remaining corruptions or check errors, flushing first so repaired metadata reaches storage before the image is marked clean. Public `qed_check()` must run with `table_lock` held and coordinates bitmap allocation, accounting, L1 traversal, leak detection, repair cleanup, and freeing temporary state.
