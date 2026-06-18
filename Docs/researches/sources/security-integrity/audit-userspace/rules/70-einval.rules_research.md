# sources/security-integrity/audit-userspace/rules/70-einval.rules

Purpose: debugging profile to find programs making syscalls with invalid parameters.

Important rules: suppresses b64 `rt_sigreturn`, then audits all syscalls with `exit=-EINVAL` and key `einval-retcode`.

Control flow: late rules intended for troubleshooting rather than production.

State and persistence: kernel audit rules.

Dependencies and integration: uses errno name parsing and broad `-S all`.

Risks and test signals: extremely noisy and may affect performance. Test with a controlled invalid syscall and search `einval-retcode`.
