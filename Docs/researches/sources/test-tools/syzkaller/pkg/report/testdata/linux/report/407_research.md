# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/407

Purpose: Linux reporter parse fixture for syzkaller. It encodes `WARNING: kobject bug in netdev_register_kobject`, type `WARNING`, corrupted `N`, panicked `Y`. The log covers a kobject duplicate/name warning during network device registration and validates that syzkaller reports the netdev registration site rather than only the kobject helper.

Important APIs, types, and functions: this static fixture is consumed by `pkg/report/report_test.go` via the Linux reporter path. Relevant parser APIs are `ContainsCrash`, `Parse`, `ParseFrom`, Linux warning/oops recognizers, and crash type mapping. Stack signals include `kobject_add_internal.cold.13`, `kobject_add`, `device_add`, `netdev_register_kobject`, `register_netdevice`, and netlink/USB execution context later in the trace.

Control flow: after headers, 88 log lines are parsed. The kernel warns in `lib/kobject.c`, escalates to panic due to `panic_on_warn`, and unwinds through network device registration. The reporter must use the header expectation and stack extraction rules to produce the netdev-specific title.

State and persistence behavior: the only persistent state is the fixture. Parser state includes matching offsets, selected frame, crash type, and panic flag; there is no I/O beyond reading the testdata.

Dependencies, integration points, risks, and test signals: this integrates the Linux kobject warning regexes with network-device deduplication. The main risk is choosing `kobject_add_internal` as the title frame, which would collapse unrelated kobject warnings. Passing tests require type `WARNING`, panic `Y`, non-corrupted output, and exact title preservation.
