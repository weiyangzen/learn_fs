<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/337 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/337

## Purpose
This fixture validates direct sysrq crash panic parsing. The expected title is `kernel panic: sysrq triggered crash`, type `DoS`, with `PANICKED: Y`.

## Important APIs, Types, And Functions
Key markers are `Kernel panic - not syncing: sysrq triggered crash`, `sysrq_handle_crash`, `__handle_sysrq`, `write_sysrq_trigger`, `proc_reg_write`, `vfs_write`, and `ksys_write`. The fixture also includes an explicit cleaned `REPORT:` block.

## Control Flow
The parser reads headers, scans the raw log, and compares the selected report with the explicit `REPORT:` section. It must preserve the sysrq panic as the root report and not over-trim the user-space write path.

## State And Persistence
Persistent state includes title/type/panic metadata plus the explicit expected report body. Runtime state is a write to the sysrq trigger from a syzkaller executor.

## Dependencies And Integration Points
It integrates with panic parsing, sysrq-specific title extraction, explicit `REPORT:` comparison in testdata, and report text normalization that strips printk prefixes.

## Risks
Because sysrq is intentional, classification must remain `DoS` rather than memory-safety or warning. Changes to report-body prefix stripping can affect the explicit report comparison.

## Test Signals
The parser should output the exact sysrq panic title and the report body beginning with `Kernel panic - not syncing: sysrq triggered crash`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/337 -->
