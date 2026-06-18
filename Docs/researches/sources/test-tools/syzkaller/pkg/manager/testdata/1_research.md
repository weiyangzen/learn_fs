# sources/test-tools/syzkaller/pkg/manager/testdata/1

Purpose: Minimal crash-report fixture containing only the syzkaller tail-report separator.

Important content: The file is effectively empty aside from `<<<<<<<<<<<<<<< tail report >>>>>>>>>>>>>>>`.

Control flow and state: `TestGetSubsystems` saves it as a report and expects no subsystem classification.

Dependencies and integration: Exercises `CrashStore.getSubsystems`, reporter parsing, and subsystem extraction when a report has no useful stack or guilty file.

Risks: Empty/minimal reports must not produce bogus subsystem matches or crash the parser.

Test signals: Negative fixture for nil subsystem output.
