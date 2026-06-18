# sources/security-integrity/audit-userspace/rules/30-ospp-v42-4-delete-success.rules

Purpose: OSPP successful delete/rename auditing.

Important rules: b32 and b64 rules for `unlink`, `unlinkat`, `rename`, and `renameat` with `success=1`, user auid filters, key `successful-delete`.

Control flow: simple exit filters.

State and persistence: kernel audit rules.

Dependencies and integration: auditctl parses syscall lists and success field.

Risks and test signals: may miss `renameat2` if that syscall is used for deletion-like changes. Test with successful unlink and ausearch key `successful-delete`.
