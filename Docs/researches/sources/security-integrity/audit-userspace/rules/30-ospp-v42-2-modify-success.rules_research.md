# sources/security-integrity/audit-userspace/rules/30-ospp-v42-2-modify-success.rules

Purpose: OSPP successful file modification auditing.

Important rules: six b32/b64 rules cover write-open variants and truncation with `success=1`, user auid filters, and key `successful-modification`.

Control flow: loads as syscall exit filters after baseline and before broader access success rules.

State and persistence: kernel audit rules.

Dependencies and integration: auditctl parses syscall lists, arch selectors, argument bit masks, and success field.

Risks and test signals: can generate substantial volume for normal writes. Validate by modifying a file as a logged-in user and querying key `successful-modification`.
