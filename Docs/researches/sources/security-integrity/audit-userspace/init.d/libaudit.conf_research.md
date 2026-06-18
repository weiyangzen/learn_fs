# sources/security-integrity/audit-userspace/init.d/libaudit.conf

Purpose: Default libaudit tunables file, currently used only for `failure_action`.

Important setting: `failure_action = ignore`, with documented allowed values `log`, `ignore`, and `terminate`.

Control flow: Declarative only; parsed by `lib/libaudit.c` through `get_auditfail_action` and `load_libaudit_config`.

State and persistence: Persistent system-level libaudit behavior under `/etc/libaudit.conf`.

Dependencies and integration: Installed by `init.d/Makefile.am` to `${sysconfdir}`. Parsed with strict ownership/permission checks in libaudit.

Risks: File must be root-owned and not writable by group/others or libaudit rejects it. Only one tunable is accepted; unknown keys are errors.

Test signals: Call `get_auditfail_action` with valid, missing, permission-bad, and unknown-key config files; validate default ignore behavior.
