<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/353 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/353

## Purpose
This fixture verifies Trusty secure-world panic title extraction for an IPC channel list assertion. The expected title is `trusty: ASSERT FAILED: !list_in_list(&chan->node)`, type `DoS`, panicked.

## Important APIs, Types, And Functions
The key Trusty marker is `ASSERT FAILED at (trusty/kernel/lib/trusty/ipc.c:472): !list_in_list(&chan->node)`, followed by `trusty: HALT`, `trusty crashed`, a Linux warning at `drivers/trusty/trusty.c:215 trusty_std_call32`, and panic-on-warn. The Linux stack includes `nop_work_func`, `process_one_work`, and `worker_thread`.

## Control Flow
The parser must recognize the Trusty panic message before the Linux wrapper warning and use the secure-world assertion text as the title. It then marks panicked from Linux panic-on-warn.

## State And Persistence
The fixture persists the Trusty title, type `DoS`, and panicked flag. Runtime state is a Trusty app-management channel failure propagated through a Linux workqueue.

## Dependencies And Integration Points
It depends on Trusty-specific report patterns, multiline panic text handling, arm64 call-trace parsing, and panic-on-warn detection.

## Risks
The generic Linux `WARNING` can obscure the more specific Trusty assertion if parser priority changes.

## Test Signals
Expected output is the full `!list_in_list(&chan->node)` assertion title with `TYPE: DoS` and `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/353 -->
