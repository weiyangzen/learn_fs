<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/356 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/356

## Purpose
This Trusty fixture checks behavior when assertion details are split across lines, leaving the expected title as the generic `trusty: ASSERT FAILED:` with corruption and panic flags.

## Important APIs, Types, And Functions
The log shows Trusty app metadata, channel wait failure, `ASSERT FAILED at ... ipc.c:472:` on one line, the assertion expression `!list_in_list(&chan->node)` on the next, then Trusty halt/crash and Linux `trusty_std_call32` panic-on-warn stack.

## Control Flow
The parser recognizes the Trusty assertion root but cannot reliably join the split assertion text for this corrupted fixture, so it keeps the generic assertion title and marks corruption. Panic state comes from the Linux panic-on-warn line.

## State And Persistence
The header persists `TYPE: DoS`, `CORRUPTED: Y`, and `PANICKED: Y`. Runtime state includes Trusty app start/channel state and Linux workqueue notification.

## Dependencies And Integration Points
It depends on Trusty assertion parsing, multiline handling, corrupted-title fallback, arm64 call-trace parsing, and panic detection.

## Risks
Future multiline-join changes could produce a more specific title, intentionally changing this regression's expected output.

## Test Signals
The stable result is generic `trusty: ASSERT FAILED:` with type `DoS`, corrupted and panicked flags.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/356 -->
