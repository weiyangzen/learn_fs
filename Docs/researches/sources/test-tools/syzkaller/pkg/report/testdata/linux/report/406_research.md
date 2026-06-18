# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/406

Purpose: Linux reporter parse fixture for syzkaller. It encodes the expected title `WARNING: refcount bug in hci_register_dev`, type `REFCOUNT_WARNING`, corrupted flag `N`, and panic signal `Y`. The raw body covers Bluetooth HCI virtual device registration hitting `refcount_t: increment on 0` through kobject/device registration, so the reporter must classify a refcount warning rather than a generic warning.

Important APIs, types, and functions: this is static testdata for `pkg/report/report_test.go`, not executable Go code. It exercises `Reporter.ContainsCrash`, `Reporter.Parse`, `Reporter.ParseFrom`, Linux oops matchers in `linux.go`, generic `Report` fields, and `crash.TitleToType`. Key stack signals include `refcount_inc_checked`, `kobject_get`, `kobject_add_internal`, `device_add`, `hci_register_dev`, `__vhci_create_device`, and `vhci_write`.

Control flow: the test harness reads expectation headers, feeds the remaining 72 log lines to the Linux reporter, and expects the title/type/panic fields to match. The call path begins with a userspace `write`, enters `vhci_write`, registers an HCI device, and panics because `panic_on_warn` follows the refcount warning.

State and persistence behavior: all persistent state is textual fixture data. Runtime state is transient parser state: selected oops, title, type, offsets, report bytes, and panic/corruption flags. No external mutation occurs.

Dependencies, integration points, risks, and test signals: the fixture protects syzkaller crash deduplication for Bluetooth/kobject refcount warnings. Risks are over-normalizing the title to `refcount_inc_checked` or losing the subsystem frame. Passing tests require crash detection, `REFCOUNT_WARNING`, panicked `Y`, non-corrupted `N`, and stable `ParseFrom` behavior.
