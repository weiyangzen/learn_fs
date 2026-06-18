# sources/test-tools/syzkaller/dashboard/app/linux_reporting.go

Purpose: small Linux-specific reporting helpers for filesystem/VFS handling and monthly report suppression.

Important APIs/types/functions: `canBeVfsBug` and `isWorthMonthlyReport`.

Control flow: `canBeVfsBug` scans subsystem labels for legacy `vfs` or current `fs`; `isWorthMonthlyReport` scans titles and returns true on the first title not starting with `INFO:`.

State/persistence: read-only over existing bug labels/titles.

Dependencies/integration: depends on `Bug.LabelValues`, `SubsystemLabel`, and string prefix matching; integrated into Linux reporting config/filter behavior.

Risks/test signals: label-based VFS detection depends on subsystem extraction; the monthly heuristic is literal and case/whitespace sensitive. `linux_reporting_test.go` covers flow and truth-table behavior.
