# sources/security-integrity/audit-userspace/rules/30-ospp-v42-4-delete-failed.rules

Purpose: OSPP unsuccessful file deletion/rename auditing.

Important rules: four b32/b64 rules for `unlink`, `unlinkat`, `rename`, and `renameat` with `-EACCES` or `-EPERM`, user auid filters, key `unsuccessful-delete`.

Control flow: loaded as exit filters in the OSPP delete group.

State and persistence: kernel audit rules.

Dependencies and integration: syscall names come from architecture tables.

Risks and test signals: does not include newer `renameat2`; depending on policy expectations that may be a gap. Test denied unlink/rename attempts and search key `unsuccessful-delete`.
