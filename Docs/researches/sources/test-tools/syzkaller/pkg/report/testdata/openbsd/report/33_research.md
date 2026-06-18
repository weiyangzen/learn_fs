# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/33

Purpose: OpenBSD witness lock-order reversal fixture. Expected title is `witness: reversal: inode netlock`; expected `SUPPRESSED: Y`.

Important parser APIs and patterns: handled by `openbsdOopses` under `lock order reversal:`. The title regex captures first and second lock names from `1st ... inode` and `2nd ... netlock`. `ctorOpenbsd` also defines a suppression regex for witness lock-order reversals with `first seen at`.

Control flow: the log starts after SSH setup and `executing program`, reports a witness reversal, prints both lock-order histories with `#0...#10` frames, then enters DDB and traces the active CPU and other CPUs.

State and persistence: static fixture preserving lock addresses, lock names, witness history, process state, and allocator tables. It represents diagnostic state rather than a kernel panic (`show panic` says the kernel did not panic).

Dependencies and integration: tests OpenBSD witness detection, title extraction, suppression policy, and stack parsing for `#N function+offset` witness frames.

Risks: witness reports are diagnostic and can be noisy; unsuppressed handling would overreport known lock-order classes. Regex must still identify lock names despite addresses and parenthesized descriptions.

Test signals: exact title `witness: reversal: inode netlock`; `SUPPRESSED: Y`; lock history contains `witness_checkorder`.
