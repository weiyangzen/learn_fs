# sources/security-integrity/audit-userspace/rules/23-ignore-filesystems.rules

Purpose: suppresses events originating from noisy pseudo filesystems during module load and tracing.

Important rules: `never,filesystem` filters for `fstype=tracefs` and `fstype=debugfs`.

Control flow: early filesystem filter rules reduce later event volume.

State and persistence: kernel filesystem filter state.

Dependencies and integration: depends on `fstype` field lookup from libaudit.

Risks and test signals: can hide activity on debug/tracing filesystems. Test by loading rules and checking `auditctl -l` for filesystem filters.
