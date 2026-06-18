# sources/security-integrity/audit-userspace/rules/11-loginuid.rules

Purpose: makes loginuid immutable so the audit user id cannot be changed after being set.

Important command: `--loginuid-immutable`, handled by `audit_set_loginuid_immutable`.

Control flow: one command loaded after baseline setup.

State and persistence: sets a kernel audit feature/lock state; changing it may require reboot or feature-specific unlock behavior.

Dependencies and integration: depends on kernel support for audit feature API and `auditctl.c` long option handling.

Risks and test signals: can break workloads that expect to reset loginuid in containers or service managers. `auditctl -s -i` or feature listing verifies state when supported.
