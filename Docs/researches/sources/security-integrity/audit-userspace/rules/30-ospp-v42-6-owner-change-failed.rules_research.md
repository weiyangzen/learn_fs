# sources/security-integrity/audit-userspace/rules/30-ospp-v42-6-owner-change-failed.rules

Purpose: OSPP unsuccessful ownership change auditing.

Important rules: four b32/b64 rules for `lchown`, `fchown`, `chown`, `fchownat`, and `file_setattr` with `-EACCES` or `-EPERM`, user filters, key `unsuccessful-owner-change`.

Control flow: exit filters for failure status.

State and persistence: kernel audit rules.

Dependencies and integration: depends on syscall lookup and errno lookup for symbolic failures.

Risks and test signals: `file_setattr` inclusion assumes newer kernel support. Test denied chown operations and search key `unsuccessful-owner-change`.
