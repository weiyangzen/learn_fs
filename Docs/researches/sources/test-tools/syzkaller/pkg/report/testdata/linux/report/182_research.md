<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/182 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/182

## Purpose
This fixture covers a kobject warning raised while enslaving a network device to a bridge. The expected title is `WARNING: kobject bug in br_add_if`, type `WARNING`, with `PANICKED: Y`. The key diagnostic line is `kobject_add_internal failed for brport (error: -12 parent: syz6)`.

## Important APIs, Types, And Functions
The fixture uses syzkaller's report-test header schema and raw kernel trace. Parser logic exercised includes warning matching, kobject-special title extraction, source-location removal from `lib/kobject.c:244`, and panic-on-warn handling. Important frames include `kobject_add_internal`, `kobject_init_and_add`, `br_add_if`, `br_add_slave`, `do_set_master`, `do_setlink`, `rtnl_newlink`, `rtnetlink_rcv_msg`, `netlink_sendmsg`, `sock_write_iter`, and `SyS_writev`.

## Control Flow
The Linux reporter scans from the kobject failure text into the cut-here warning, then follows the stack from rtnetlink writev handling into bridge configuration. The expected title uses the higher-level bridge function `br_add_if`, not only the low-level kobject helper. The panic flag is derived from `Kernel panic - not syncing: panic_on_warn set ...`.

## State And Persistence
The checked-in file persists expected metadata and a 138-line trace. Runtime state represented in the log includes netdevice names, netlink socket state, PIDs, register values, and memory addresses; these are parser input only and should not be treated as stable state.

## Dependencies And Integration Points
It integrates with Linux report parsing, warning-title heuristics, bridge/rtnetlink stack recognition, and panic detection. The test relies on the reporter preserving enough context to classify the warning as a bridge kobject bug.

## Risks
Parser regressions may title this as `WARNING in kobject_add_internal`, miss `br_add_if`, or fail to handle the pre-warning diagnostic line. Because the trace is a network configuration path, many optional helper frames appear and should not perturb the title.

## Test Signals
The stable test signal is title `WARNING: kobject bug in br_add_if`, type `WARNING`, panic true, and report text containing both `kobject_add_internal failed for brport` and the bridge/rtnetlink call chain.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/182 -->
