# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/432

Purpose: Linux reporter parse fixture for syzkaller. It expects `INFO: task hung in synchronize_rcu`, alternates for `synchronize_rcu_expedited`, type `HANG`, corrupted `N`, panicked `Y`. The log covers network namespace tunnel cleanup blocked in expedited RCU synchronization.

Important APIs, types, and functions: this tests hung-task parsing where generic synchronization APIs are intentionally the title. Frames include `synchronize_rcu_expedited`, `synchronize_net`, `rollback_registered_many`, `unregister_netdevice_many`, `ip_tunnel_delete_nets`, `ipip_exit_batch_net`, and `cleanup_net`.

Control flow: 316 log lines include a blocked cleanup worker and lock debug output. The parser must normalize expedited and non-expedited RCU hang alternates while preserving panic-on-hung-task.

State and persistence behavior: headers persist multiple alternates and panic flag. Runtime state is hang detection and selected frame metadata.

Dependencies, integration points, risks, and test signals: this protects RCU hang grouping in network teardown. Risks include choosing tunnel-specific frames when the expected dedup key is synchronization. Passing tests require all alternates, HANG type, panic `Y`, and no corruption.
