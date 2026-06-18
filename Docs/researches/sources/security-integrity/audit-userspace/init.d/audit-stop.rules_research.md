# sources/security-integrity/audit-userspace/init.d/audit-stop.rules

Purpose: Optional auditctl rules file used when administrators want audit rules cleared as auditd stops.

Important commands: `-e 0` disables auditing; `-D` deletes all audit rules.

Control flow: No script control flow. If referenced by the commented `ExecStopPost` in `audit-rules.service.in` or manually loaded with `auditctl -R`, auditctl applies commands in order.

State and persistence: Mutates kernel audit state by disabling auditing and deleting rules. Does not persist state beyond kernel runtime except by being installed as a config file.

Dependencies and integration: Installed with `auditd.conf` under `/etc/audit` by `init.d/Makefile.am`. Intended for `auditctl`.

Risks: Loading this file removes audit coverage. It should remain opt-in and protected by root-owned config permissions.

Test signals: In a controlled VM, run `auditctl -R audit-stop.rules` and confirm `auditctl -s` shows disabled state and `auditctl -l` is empty.
