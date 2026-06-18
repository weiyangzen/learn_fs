# sources/security-integrity/audit-userspace/init.d/audit-tmpfiles.conf

Purpose: systemd-tmpfiles declaration that creates the audit log directory.

Important entry: `d /var/log/audit 0700 root root - -` creates `/var/log/audit` as a root-owned directory with mode 0700.

Control flow: Declarative only; systemd-tmpfiles processes it during boot or manual tmpfiles creation.

State and persistence: Ensures persistent log directory exists with restrictive permissions.

Dependencies and integration: Installed as `audit.conf` in the tmpfiles.d directory by `init.d/Makefile.am`. `auditd.service.in` and `audit-rules.service.in` order after `systemd-tmpfiles-setup.service`.

Risks: Incorrect permissions would expose audit logs. The hard-coded `/var/log/audit` must match `auditd.conf` `log_file` default and packaging expectations.

Test signals: `systemd-tmpfiles --create audit.conf`, then check directory ownership/mode and auditd log write success.
