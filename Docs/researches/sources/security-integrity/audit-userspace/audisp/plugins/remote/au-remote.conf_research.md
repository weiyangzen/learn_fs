# sources/security-integrity/audit-userspace/audisp/plugins/remote/au-remote.conf

Purpose: audisp plugin registration file for the remote audit event logger.

Important APIs and data: sets `active = no`, `path = /sbin/audisp-remote`, `type = always`, and `format = string`.

Control flow: audit dispatcher reads this to decide whether and how to launch `audisp-remote`.

State and persistence: installed under audit plugin config and persists until changed by administrator.

Dependencies and integration: points dispatcher output to the remote plugin, whose own settings are in `audisp-remote.conf`.

Risks: disabled by default; enabling without a valid remote config can stall or stop remote logging depending failure actions.

Test signals: dispatcher config parsing and plugin activation tests.
