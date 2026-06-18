# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/439

Purpose: Linux reporter parse fixture for syzkaller. It expects `INFO: task hung in synchronize_rcu` with expedited alternates, type `HANG`, corrupted `N`, panicked `Y`. The body covers filesystem/superblock shutdown and backing-device unregister blocked in expedited RCU.

Important APIs, types, and functions: key frames include `synchronize_rcu_expedited`, `bdi_unregister`, `bdi_put`, `generic_shutdown_super`, `fuse_kill_sb_anon`, `deactivate_super`, and mount cleanup helpers.

Control flow: 76 log lines are parsed. The reporter must select the synchronization hang, not the FUSE or BDI teardown callers, and preserve panic-on-hung-task.

State and persistence behavior: expected output persists in headers; runtime state is temporary parse metadata.

Dependencies, integration points, risks, and test signals: this protects cross-subsystem RCU hang grouping outside networking. Risks include caller-specific titles and lost alternates. Passing tests require all expected alternates, HANG type, panic `Y`, and non-corruption.
