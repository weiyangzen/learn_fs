<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/344 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/344

## Purpose
This fixture covers stack guard page overflow detection in a corrupted recursive IPv6 error path. The expected title is `BUG: stack guard page was hit in corrupted`, with alt `stack-overflow in corrupted`, corrupted and panicked.

## Important APIs, Types, And Functions
The leading markers are `BUG: stack guard page was hit` and `kernel stack overflow (double-fault)`. The visible RIP is `__udp6_lib_lookup`, followed by many recursive `__udp6_lib_err`, `udplitev6_err`, and `gue6_err` frames before networking receive and ksoftirqd frames.

## Control Flow
The parser must recognize stack-guard overflow as the primary oops and fall back to `corrupted` because the recursive trace and overflow state make specific function attribution unreliable. It sets panic from `Kernel panic - not syncing: Fatal exception in interrupt`.

## State And Persistence
Persistent state is title/alt/corrupted/panicked metadata. The raw log preserves stack range, double-fault registers, softirq context, and reboot line.

## Dependencies And Integration Points
It depends on stack-guard page patterns, stack-overflow alt generation, recursive stack trimming, and interrupt panic detection.

## Risks
The parser could select `__udp6_lib_lookup` as a precise title, but the expected behavior is conservative due to corruption.

## Test Signals
Expected output keeps `BUG: stack guard page was hit in corrupted`, alt `stack-overflow in corrupted`, and both flags.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/344 -->
