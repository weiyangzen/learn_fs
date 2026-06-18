# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/414

Purpose: Linux reporter parse fixture for syzkaller. It expects `KASAN: use-after-free Write in iowarrior_disconnect`, alternate `bad-access in iowarrior_disconnect`, type `KASAN-USE-AFTER-FREE-WRITE`, corrupted `N`, panicked `N`. The body is a write UAF in USB URB teardown during IOWarrior disconnect.

Important APIs, types, and functions: this fixture exercises KASAN write classification and USB disconnect frame selection. Important frames include `usb_kill_urb`, `check_memory_region`, `iowarrior_disconnect`, `usb_unbind_interface`, `device_release_driver_internal`, and `device_del`.

Control flow: the parser consumes 109 log lines, recognizes the KASAN UAF report, infers write access, and attributes it to `iowarrior_disconnect` rather than `usb_kill_urb`.

State and persistence behavior: the file persists headers and console text. Runtime parser state is temporary report metadata and flags.

Dependencies, integration points, risks, and test signals: this pairs with report 413 and checks read/write distinctions for the same disconnect path. The key risk is losing access direction or over-grouping under USB core helpers. Passing tests require UAF-write type and the exact title/alternate.
