# sources/security-integrity/audit-userspace/rules/30-ospp-v42-1-create-failed.rules

Purpose: OSPP v4.2 unsuccessful file creation auditing for `open*` with `O_CREAT` and `creat`.

Important rules: 12 b32/b64 rules covering `openat`, `open_by_handle_at`, `open`, and `creat` with exits `-EACCES` and `-EPERM`, user filters `auid>=1000` and `auid!=unset`, key `unsuccessful-create`.

Control flow: should precede broader failed access rules so create failures get the more specific key.

State and persistence: kernel exit filter rules.

Dependencies and integration: syscall numbers and octal argument masks are parsed by auditctl/libaudit.

Risks and test signals: argument positions differ between `open` and `openat`, which this file handles separately. Test with denied create attempts and ausearch key `unsuccessful-create`.
