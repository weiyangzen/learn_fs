# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/423

Purpose: Linux reporter parse fixture for syzkaller. It expects `KASAN: use-after-free Read in mcba_usb_disconnect`, alternate `bad-access in mcba_usb_disconnect`, type `KASAN-USE-AFTER-FREE-READ`, corrupted `N`, panicked `N`. The report covers CAN MCBA USB disconnect while anchored URBs and locks are being torn down.

Important APIs, types, and functions: this tests KASAN read UAF extraction and USB driver frame selection. Key frames include `__lock_acquire`, `usb_kill_anchored_urbs`, `mcba_usb_disconnect`, `usb_unbind_interface`, and `device_release_driver_internal`.

Control flow: 95 log lines are parsed. The parser must skip lockdep internals and assign the crash to the MCBA USB disconnect callback.

State and persistence behavior: fixture text persists expected fields; parser runtime state is temporary.

Dependencies, integration points, risks, and test signals: this protects CAN/USB disconnect grouping and bad-access alternate generation. Risks include title drift to `__lock_acquire` or USB core helpers. Passing tests require UAF-read type, expected title/alternate, no panic, and no corruption.
