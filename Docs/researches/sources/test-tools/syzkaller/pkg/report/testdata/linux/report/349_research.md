<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/349 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/349

## Purpose
This fixture validates hung-task parsing for ext4/jbd2 journal commits. The expected title is `INFO: task hung in jbd2_journal_commit_transaction`, alt `hang in jbd2_journal_commit_transaction`, type `HANG`, and panicked.

## Important APIs, Types, And Functions
The root marker is `INFO: task jbd2/sda-8:3563 blocked for more than 140 seconds`. The first stack contains `__wait_on_buffer` and `jbd2_journal_commit_transaction`; a second blocked writeback worker includes `wbt_wait`, block I/O, `ext4_writepages`, and `wb_workfn`.

## Control Flow
The parser must choose the first hung-task report and title it from the blocked task's meaningful stack, not from later writeback worker hangs. Panic is inferred from later hung-task panic/reboot context.

## State And Persistence
The fixture stores expected hang metadata and the raw multi-task blocked report. Runtime state is journal and writeback I/O waiting.

## Dependencies And Integration Points
It depends on hung-task recognizers, blocked-task stack selection, alt generation for `hang in`, and panic detection.

## Risks
Multiple blocked tasks can cause unstable title selection if ordering or stack scoring changes.

## Test Signals
The parser must preserve `jbd2_journal_commit_transaction` as the title function and classify as `HANG`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/349 -->
