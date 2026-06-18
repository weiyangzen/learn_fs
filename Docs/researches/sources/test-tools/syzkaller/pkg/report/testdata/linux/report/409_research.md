# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/409

Purpose: Linux reporter parse fixture for syzkaller. It expects `WARNING: ODEBUG bug in usbhid_disconnect`, type `WARNING`, corrupted `N`, panicked `Y`. The raw log is a debugobjects report for freeing an active `timer_list` with hint `hid_retry_timeout` during USB HID disconnect.

Important APIs, types, and functions: the fixture exercises Linux ODEBUG warning parsing. Relevant syzkaller APIs are the standard report test harness and Linux warning recognizers. Important frames include `debug_print_object`, `debug_check_no_obj_freed`, `__free_pages_ok`, and `usbhid_disconnect`.

Control flow: the parser sees an `ODEBUG: free active` line, the subsequent `WARNING`, and a panic-on-warn stack. It must attribute the report to `usbhid_disconnect`, not the generic debugobjects or memory-freeing helpers.

State and persistence behavior: static headers persist title/type/panic expectations. Parser state records the selected crash span and frame but no external state is changed.

Dependencies, integration points, risks, and test signals: this integrates debugobjects warnings with USB HID teardown grouping. The risk is treating the hint `hid_retry_timeout` as the primary title or losing disconnect context. Passing tests require a warning type, panic `Y`, non-corrupted report, and the expected ODEBUG title.
