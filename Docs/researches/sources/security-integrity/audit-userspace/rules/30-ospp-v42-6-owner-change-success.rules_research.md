# sources/security-integrity/audit-userspace/rules/30-ospp-v42-6-owner-change-success.rules

Purpose: OSPP successful ownership change auditing.

Important rules: b32 and b64 rules for chown family plus `file_setattr` with `success=1`, user filters, key `successful-owner-change`.

Control flow: exit filters loaded in the OSPP owner-change group.

State and persistence: kernel audit rules.

Dependencies and integration: uses auditctl syscall list parsing and auid filters.

Risks and test signals: may be noisy on administrative systems. Test with successful chown as a logged-in administrative user and query key `successful-owner-change`.
