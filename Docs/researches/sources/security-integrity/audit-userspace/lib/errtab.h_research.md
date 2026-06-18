# sources/security-integrity/audit-userspace/lib/errtab.h

Purpose: Lookup input mapping errno constants to symbolic names for audit rule parsing and display.

Important entries: Covers generic Linux errno-base and errno values from `EPERM` through `EHWPOISON`, including duplicate aliases such as `EWOULDBLOCK` and `EDEADLOCK`.

Control flow: No runtime control flow; `gen_errtabs_h` generates uppercase string-to-int and int-to-string helpers with duplicate integer support.

State and persistence: Static mapping compiled into libaudit.

Dependencies and integration: Depends on system errno constants from headers. Used by `audit_name_to_errno`, `audit_errno_to_name`, and `AUDIT_EXIT` field parsing.

Risks: Errno numeric values can vary on some architectures. The comment notes generic asm headers are the source, so portability must be verified. Duplicate aliases need `--duplicate-ints` or generation aborts.

Test signals: Round-trip tests for common errnos and aliases, and architecture build checks.
