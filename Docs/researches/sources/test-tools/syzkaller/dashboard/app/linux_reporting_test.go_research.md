# sources/test-tools/syzkaller/dashboard/app/linux_reporting_test.go

Purpose: validates Linux filesystem reporting policy and monthly report worthiness.

Important APIs/types/functions: `TestFsSubsystemFlow`, `TestVfsSubsystemFlow`, and `TestIsWorthMonthlyReport`.

Control flow: tests upload builds and crashes with guilty files/repros, verify non-fs immediate reporting, filesystem-specific recipient selection, delayed possible-VFS reporting, repro-triggered subsystem refinement, and fallback generic fs reporting. Table tests cover all-INFO, mixed, non-INFO, and empty bug lists.

State/persistence: persists builds, crashes, bug labels, reporting stages, notifications, and emails in the test context.

Dependencies/integration: integrates subsystem extraction, syz repro parsing, reporting filters, email recipient selection, notification polling, and Linux helpers.

Risks/test signals: expected maintainer lists are sensitive to subsystem metadata/config. Signals include exact email subjects, recipient sets, and monthly-report boolean outcomes.
