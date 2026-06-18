# sources/test-tools/syzkaller/pkg/manager/testdata/3

Purpose: Crash-report fixture for memory-management subsystem extraction.

Important content: The report centers on `WARNING: mm/rmap.c:528 at unlink_anon_vmas`, with stack frames through `free_pgtables`, `exit_mmap`, and related `mm/` paths.

Control flow and state: Used by `TestGetSubsystems`, which expects subsystem `mm`.

Dependencies and integration: Verifies that warning-style reports with file/line titles can be parsed into a guilty file and matched against subsystem path rules.

Risks: The fixture starts mid-log before the warning marker, so parser resilience to partial preceding context matters. If guilty-file ranking changes, subsystem extraction may change.

Test signals: Positive fixture for `mm/` path classification.
