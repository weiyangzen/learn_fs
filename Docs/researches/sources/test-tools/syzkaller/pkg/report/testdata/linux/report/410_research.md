# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/410

Purpose: Linux reporter parse fixture for syzkaller. It expects `KASAN: use-after-free Read in hiddev_read`, alternate `bad-access in hiddev_read`, type `KASAN-USE-AFTER-FREE-READ`, corrupted `N`, panicked `N`. The body covers a KASAN read UAF surfaced while HID device userspace reads are finishing wait/lock handling.

Important APIs, types, and functions: this fixture exercises KASAN parsing, access-mode classification, alternate title creation, and frame selection. Key frames include `__lock_acquire`, `kasan_report`, `finish_wait`, `hiddev_read`, `__vfs_read`, and `vfs_read`.

Control flow: 153 log lines are fed to the reporter. The KASAN report first names a lockdep/internal access, but the expected title is the higher-level HID read site. The parser must extract read direction and UAF type while retaining the subsystem frame.

State and persistence behavior: the fixture stores expected fields; runtime state is report-byte boundaries, KASAN metadata, selected frame, and alternate title.

Dependencies, integration points, risks, and test signals: this protects KASAN crash deduplication for HID char-device read paths. Risks include selecting `__lock_acquire` or losing the `Read` access direction. Passing tests require exact title, bad-access alternate, UAF-read type, and non-panicked/non-corrupted flags.
