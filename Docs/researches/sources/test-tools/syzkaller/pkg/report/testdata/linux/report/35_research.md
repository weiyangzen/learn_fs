<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/35 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/35

## Purpose
This fixture verifies suspicious RCU usage parsing with an explicit `START:` directive. The expected title is `INFO: suspicious RCU usage in corrupted`.

## Important APIs, Types, And Functions
The important parser contract includes `START: [   37.540478] [ INFO: suspicious RCU usage. ]`, which tells the test harness where the expected report begins. The visible stack includes `vcpu_load+0x22/0x70`, but corruption prevents precise title attribution.

## Control Flow
After reading headers, the test harness uses the `START` marker to align expected report extraction. The Linux reporter detects the RCU info banner and emits the corrupted fallback title.

## State And Persistence
Persistent metadata includes title, start marker, and `CORRUPTED: Y`. The raw log is a short RCU splat excerpt.

## Dependencies And Integration Points
It depends on the testdata `START` directive, RCU warning pattern recognition, and corrupted-title fallback.

## Risks
Changes to prefix matching for `START` or RCU banners could make the fixture fail even though the raw report is small.

## Test Signals
The parser should start at the given line and produce `INFO: suspicious RCU usage in corrupted`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/35 -->
