# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/422

Purpose: Linux reporter parse fixture for syzkaller. It expects `KASAN: use-after-free Read in hso_probe`, alternate `bad-access in hso_probe`, type `KASAN-USE-AFTER-FREE-READ`, corrupted `N`, panicked `N`. The body covers HSO USB serial probing and tty device unregister/destruction lifetime issues.

Important APIs, types, and functions: this tests KASAN read UAF parsing in probe paths. Significant frames include `__mutex_lock`, `device_del`, `device_destroy`, `tty_unregister_device`, `hso_probe.cold`, `usb_probe_interface`, and `really_probe`.

Control flow: 173 log lines are parsed. The report names a low-level mutex access, but the expected title is the driver probe function where teardown/probe sequencing is meaningful.

State and persistence behavior: fixture headers are persistent; parser state is transient KASAN metadata, selected frame, and flags.

Dependencies, integration points, risks, and test signals: this protects USB serial probe crash grouping. Risks include selecting `__mutex_lock` or tty core helpers. Passing tests require exact title, bad-access alternate, UAF-read type, and no panic/corruption.
