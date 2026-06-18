# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/418

Purpose: Linux reporter parse fixture for syzkaller. It expects `general protection fault in hdm_disconnect`, alternate `bad-access in hdm_disconnect`, type `DoS`, corrupted `N`, panicked `Y`. The log covers a GPF during MOST HDM USB disconnect.

Important APIs, types, and functions: this static report tests non-KASAN bad-access title extraction. Significant frames include `device_unregister`, `hdm_disconnect`, `usb_unbind_interface`, `device_release_driver_internal`, `usb_disconnect`, `hub_event`, and worker thread helpers.

Control flow: 60 log lines are parsed. The exception is fatal and escalates to panic, and the reporter must classify it as DoS while generating the bad-access alternate.

State and persistence behavior: fixture text holds expected state. Runtime state is selected oops, frame, flags, and report boundaries.

Dependencies, integration points, risks, and test signals: this supports syzkaller grouping for USB disconnect GPFs. Risks include selecting `device_unregister` or `usb_unbind_interface` instead of `hdm_disconnect`. Passing tests require the GPF title, DoS type, alternate, and panic flag.
