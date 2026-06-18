# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/411

Purpose: Linux reporter parse fixture for syzkaller. It expects `WARNING in r871xu_dev_remove`, type `WARNING`, corrupted `N`, panicked `Y`. The raw report is a network-core unregister warning reached during Realtek USB wireless device removal.

Important APIs, types, and functions: the fixture exercises warning parsing and subsystem frame extraction. Significant frames include `rollback_registered_many.cold`, `rollback_registered`, `unregister_netdevice_queue`, `unregister_netdev`, and `r871xu_dev_remove`.

Control flow: the test feeds 77 log lines. A warning at `net/core/dev.c` panics; stack extraction must walk past generic unregister helpers to the driver removal function.

State and persistence behavior: only fixture headers and raw console text persist. Runtime parser state is transient and determines title/type/panic/corruption.

Dependencies, integration points, risks, and test signals: this integrates Linux warning handling with USB network driver teardown reports. The risk is grouping under `rollback_registered_many` instead of the driver function. Passing tests require the expected title, warning type, panic flag, and no corruption.
