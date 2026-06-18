# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/412

Purpose: Linux reporter parse fixture for syzkaller. It expects `WARNING in default_device_exit_batch`, type `WARNING`, corrupted `N`, panicked `Y`. The body covers network namespace cleanup warning during default device exit batching.

Important APIs, types, and functions: this fixture tests Linux warning stack extraction. Key frames include `rollback_registered_many`, `unregister_netdevice_many`, `default_device_exit_batch`, `ops_exit_list.isra.5`, and `cleanup_net`.

Control flow: 108 log lines are parsed after headers. The warning is emitted in network-core unregister code and escalates via panic-on-warn, while the expected title points to namespace cleanup's `default_device_exit_batch`.

State and persistence behavior: all state is fixture text plus transient parser fields. There is no persistence beyond the source file.

Dependencies, integration points, risks, and test signals: this supports syzkaller grouping for net namespace teardown warnings. Risks are overfitting to the warning source line or selecting generic cleanup helpers. Passing tests require type `WARNING`, panicked `Y`, non-corrupted `N`, and the expected title.
