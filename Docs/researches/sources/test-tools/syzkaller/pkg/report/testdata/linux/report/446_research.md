# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/446

Purpose: golden fixture for a TLS socket close hang. Expected title is `INFO: task hung in tls_sw_free_resources_tx`, alternate title is `hang in tls_sw_free_resources_tx`, type is `HANG`, and `PANICKED: Y`.

Important APIs, types, and functions: syzkaller report parsing uses the standard header contract and panic recognition. Kernel frames include `wait_for_completion`, `__flush_work`, `__cancel_work_timer`, `cancel_delayed_work_sync`, `tls_sw_free_resources_tx`, `tls_sk_proto_close`, `inet_release`, `__sock_release`, and `sock_close`.

Control flow: the blocked task waits while synchronously canceling delayed TLS transmit work during socket release. After lock inventory and NMI backtrace, the kernel panics on hung tasks. Parser flow must title the hang from `tls_sw_free_resources_tx` rather than scheduler, workqueue, or panic frames.

State and persistence behavior: static fixture persists the panic outcome and lock snapshot. It does not model runtime state beyond the reported pending work and socket close stack.

Dependencies and integration points: depends on Linux hung-task and panic parsing, plus frame filtering that skips generic completion and workqueue cancellation helpers. It integrates kernel TLS teardown into syzkaller parser coverage.

Risks: many frames are generic workqueue synchronization helpers; title extraction must descend far enough to the TLS-specific function. Panic tail must set `Panicked` without replacing the hang title.

Test signals: `cancel_delayed_work_sync`, `tls_sw_free_resources_tx+0x1df/0xcf0`, `tls_sk_proto_close+0x602/0x750`, and `Kernel panic - not syncing: hung_task: blocked tasks`.
