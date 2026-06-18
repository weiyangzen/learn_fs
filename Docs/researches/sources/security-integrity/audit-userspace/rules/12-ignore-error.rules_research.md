# sources/security-integrity/audit-userspace/rules/12-ignore-error.rules

Purpose: changes rules-file loading so auditctl continues across bad rules and exits success.

Important command: `-i`.

Control flow: `opt_ignore` sets `ignore=1`; `fileopt` continues after errors without final failure unless other fatal file errors occur.

State and persistence: process-local loader behavior only.

Dependencies and integration: consumed by `auditctl.c` when reading `-R` files.

Risks and test signals: can hide missing audit coverage on kernels without newer fields. Test with an intentionally unsupported rule and check exit status remains zero.
