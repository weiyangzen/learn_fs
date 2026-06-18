# sources/security-integrity/audit-userspace/contrib/plugin/audisp-example.conf

Purpose: Example audit plugin configuration for the manual `audisp-example` sample.

Important fields: `active = no`, `path = /sbin/audisp-example`, `type = always`, `args = 1`, and `format = string`.

Control flow: Declarative only; auditd plugin manager reads it to decide plugin activation and event delivery format.

State and persistence: Persistent plugin config if installed. Inactive by default to prevent accidental sample execution.

Dependencies and integration: Integrates with auditd plugin config syntax and the sample binary built from `contrib/plugin/audisp-example.c`.

Risks: Comment text calls it an example syslog plugin even though the code prints to stdout. The hard-coded path may be wrong for current systems, and enabling it without the binary causes auditd plugin errors.

Test signals: Enable in a test audit plugin directory, reconfigure auditd, and confirm the sample starts and receives string events.
