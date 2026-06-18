<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/197 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/197

## Purpose
This fixture validates KASAN global-out-of-bounds parsing in `/proc` timer display logic. It expects title `KASAN: global-out-of-bounds Read in show_timer`, alt `bad-access in show_timer`, type `KASAN-READ`, and `PANICKED: Y`.

## Important APIs, Types, And Functions
The fixture data includes a KASAN report and a later fatal interrupt panic. Parser behavior includes global-out-of-bounds recognition, read classification, panic detection, and mixed network noise tolerance. Important frames include `show_timer`, `seq_read`, `do_loop_readv_writev`, `do_readv_writev`, `vfs_readv`, `SyS_preadv`, plus unrelated UDP frames such as `udp_queue_rcv_skb`, `udp_sendmsg`, `inet_sendmsg`, `sock_sendmsg`, and `SyS_sendto`.

## Control Flow
The parser should select the KASAN report in `show_timer` as the primary crash. The runtime path for the primary bug is reading a seq_file timer representation, while the log also includes interrupt/network activity and a panic line. The expected panic flag comes from `Kernel panic - not syncing: Fatal exception in interrupt`.

## State And Persistence
Static state is the expected metadata and 109-line console log. Volatile state includes timer/global symbol addresses, UDP packet context, and register dumps.

## Dependencies And Integration Points
It integrates with KASAN out-of-bounds parsers, panic detection, and report-boundary logic that ignores unrelated network call traces. The fixture is consumed by syzkaller's Linux report parser tests.

## Risks
Mixed interrupt/network stack text can cause wrong title selection, such as `udp_queue_rcv_skb`. Parser logic must also preserve the KASAN-specific `KASAN-READ` type rather than broad memory-safety classification.

## Test Signals
Assert title `KASAN: global-out-of-bounds Read in show_timer`, alt `bad-access in show_timer`, type `KASAN-READ`, and panic true. The report should include `show_timer` and seq_file read frames.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/197 -->
