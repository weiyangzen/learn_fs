# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/35

Purpose: OpenBSD witness lock-order fixture where detailed order history is missing. Expected title is `witness: reversal: lock order data missing`.

Important parser APIs and patterns: the `lock order reversal:` oops group has a special title regex for `lock order data .* missing`, formatted as `witness: reversal: lock order data missing`. This rule should take precedence over the generic two-lock-name formatter.

Control flow: the log begins with `witness: lock order reversal`, lists `fdlock` then `inode`, immediately reports both `w2 -> w1` and `w1 -> w2` data missing, then enters DDB. The stack includes `witness_checkorder`, lock acquisition functions, vnode lookup, `ktrwriteraw`, `ktrstruct`, `sys_socketpair`, and syscall. Later CPU traces and pool data follow.

State and persistence: static diagnostic fixture with lock state, process tables, and allocator statistics. It is not a panic; `show panic` says the kernel did not panic.

Dependencies and integration: validates witness special-case title extraction and BSD stack handling for diagnostic reports.

Risks: if the generic reversal regex runs first, title could become `fdlock inode`, losing the important missing-history signal. Long DDB output can also affect report boundaries.

Test signals: exact title `witness: reversal: lock order data missing`; stack includes `witness_checkorder+0x108b`.
