# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/442

Purpose: golden fixture for a hung task in `synchronize_rcu`/`synchronize_sched` that escalates to a hung-task panic. Expected title is `INFO: task hung in synchronize_rcu`, alternate titles include both `synchronize_rcu` and legacy `synchronize_sched` forms, type is `HANG`, and `PANICKED: Y`.

Important APIs, types, and functions: parser APIs are the same `ParseTest` header contract and `Reporter.Parse` path. Kernel frames include `wait_for_completion`, `__wait_rcu_gp`, `synchronize_sched.part.0`, `synchronize_sched`, `synchronize_net`, `packet_release`, `__sock_release`, plus a secondary CPU backtrace in `tc_new_tfilter` via `rtnetlink_rcv_msg`.

Control flow: the log starts from a blocked packet socket release waiting for an RCU grace period. It then prints held locks, NMI backtraces, a contending netlink/tc stack, and finally `Kernel panic - not syncing: hung_task: blocked tasks`. The parser must still classify the root as a hang in RCU synchronization rather than the final panic or the unrelated NMI frame.

State and persistence behavior: persistent state is the panicked flag in the header and the raw panic tail. No mutable test state exists, but `PANICKED: Y` verifies that `linuxPanickedRe` is detected independently from title extraction.

Dependencies and integration points: depends on Linux RCU/hung-task report matchers, panic detection, and alternate-title generation that preserves older `synchronize_sched` naming. It integrates packet socket release and traffic-control netlink stacks into parser regression coverage.

Risks: kernel versions and function names may drift from `synchronize_sched` to `synchronize_rcu`; losing alternate titles would break deduplication across versions. NMI backtrace content can also distract guilty-frame selection.

Test signals: blocked `syz-executor.0`, `packet_release+0x978/0xc30`, `synchronize_net+0x4d/0x60`, NMI frame `tc_new_tfilter`, and `Kernel panic - not syncing: hung_task: blocked tasks`.
