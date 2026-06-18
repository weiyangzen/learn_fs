# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/10

## Purpose

This OpenBSD fixture expects `witness: reversal: vmmaplk inode` and is marked `SUPPRESSED: Y`. It captures a WITNESS lock-order reversal between the VM map lock and an inode lock, without a kernel panic.

## Important APIs, Types, and Functions

Reporter behaviors include witness diagnostic recognition, suppressed metadata handling, lock-name title construction, DDB parsing where `show panic` says the kernel did not panic, and trace capture. Kernel functions include `witness_checkorder`, `_rw_enter`, `vm_map_lock_ln`, `uvm_map`, `km_alloc`, `pool_get`, `ufsdirhash_build`, `ufs_lookup`, `_rrw_enter`, `VOP_LOCK`, `vn_lock`, `uvn_io`, `uvn_get`, `uvm_fault`, `uvm_fault_wire`, `uvm_map_pageable_wire`, and `sys_mlockall`.

## Control Flow

WITNESS reports two observed lock orders: inode to VM map from UFS lookup and VM map to inode from `mlockall` wiring a vnode-backed fault. It enters DDB through `witness_checkorder`, but `show panic` confirms this is a debugger break rather than a panic. The parser must still extract the witness report and title it from the two lock classes.

## State and Persistence Behavior

The fixture stores lock addresses, lock class names, source locations, two historical order stacks, DDB registers, process tables, and allocator/pool summaries. The stable state is the lock pair `vmmaplk inode`; addresses and counts are volatile.

## Dependencies and Integration Points

This integrates OpenBSD WITNESS lock-order diagnostics with suppression handling. It matters for syzkaller triage because suppressed reports should be detected but not treated with the same priority as unsuppressed crashes.

## Risks and Edge Cases

The absence of `panic:` can cause under-detection if the parser only watches panic lines. Conversely, generic DDB stops must not be reported unless preceded by WITNESS content. The title must use lock class names rather than full source paths or addresses.

## Test Signals

A passing test returns `witness: reversal: vmmaplk inode`, marks the report suppressed, and includes both lock-order stacks plus the `the kernel did not panic` DDB evidence.
