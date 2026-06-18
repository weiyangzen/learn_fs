# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/417

Purpose: Linux reporter parse fixture for syzkaller. It expects `KASAN: use-after-free Read in usbvision_release`, alternate `bad-access in usbvision_release`, type `KASAN-USE-AFTER-FREE-READ`, corrupted `N`, panicked `N`. The body covers sysfs file removal after USBVision device release.

Important APIs, types, and functions: this fixture targets KASAN read UAF extraction. Key frames include `sysfs_remove_file_ns`, `device_remove_file`, `usbvision_release`, `usbvision_radio_close.cold`, `v4l2_release`, `__fput`, and `task_work_run`.

Control flow: the harness parses 103 log lines, recognizes KASAN UAF-read metadata, and selects `usbvision_release` as the meaningful frame above sysfs/device helpers.

State and persistence behavior: only the fixture persists; parser fields are in-memory.

Dependencies, integration points, risks, and test signals: this protects media/USB release crash grouping. Risks include selecting sysfs helpers or losing release context. Passing tests require exact title, alternate, UAF-read type, no panic, and no corruption.
