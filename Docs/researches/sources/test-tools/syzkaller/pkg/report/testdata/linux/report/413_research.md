# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/413

Purpose: Linux reporter parse fixture for syzkaller. It expects `KASAN: use-after-free Read in iowarrior_disconnect`, alternate `bad-access in iowarrior_disconnect`, type `KASAN-USE-AFTER-FREE-READ`, corrupted `N`, panicked `N`. The log covers an IOWarrior USB disconnect path racing with mutex/list state.

Important APIs, types, and functions: this tests KASAN read UAF title extraction. Relevant frames include `__list_del_entry_valid`, `mutex_remove_waiter`, `__mutex_lock`, `iowarrior_disconnect`, `usb_unbind_interface`, and driver core removal helpers.

Control flow: 111 log lines are parsed. Although the low-level invalid access is in list/mutex helpers, the reporter must attribute the crash to the USB driver disconnect function and generate the bad-access alternate.

State and persistence behavior: expected parser output is stored in headers. Runtime state includes selected KASAN metadata, title frame, and report span.

Dependencies, integration points, risks, and test signals: this protects KASAN grouping for USB driver disconnect races. Risks include selecting `__list_del_entry_valid` as the title. Passing tests require exact title, alternate, UAF-read type, no panic, and no corruption.
