<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/345 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/345

## Purpose
This fixture verifies warning parsing for XFRM namespace cleanup. The expected title is `WARNING in xfrm_state_fini`, type `WARNING`, with panicked flag.

## Important APIs, Types, And Functions
The key warning is at `net/xfrm/xfrm_state.c:2381 xfrm_state_fini+0x440/0x5c0`. The cleanup stack includes `xfrm_net_exit`, `ops_exit_list.isra.0`, `cleanup_net`, `process_one_work`, and worker thread frames.

## Control Flow
The parser must locate the warning after earlier setup/fault-injection noise and select the XFRM cleanup function. It also detects `panic_on_warn set` as the panicked state.

## State And Persistence
The fixture persists warning type and panic metadata. Runtime state includes network namespace teardown on the `netns` workqueue.

## Dependencies And Integration Points
It depends on warning-at-file-line parsing, symbol extraction from RIP, workqueue context handling, and panic-on-warn detection.

## Risks
Preceding allocation failure or netdevice-event traces could be mistaken for the root report.

## Test Signals
Parser output should be `WARNING in xfrm_state_fini`, `TYPE: WARNING`, `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/345 -->
