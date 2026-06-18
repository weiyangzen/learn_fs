# sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-config.c

Purpose: parses the z/OS remote plugin's LDAP/RACF configuration file.

Important APIs and data: exports `plugin_clear_config`, `plugin_load_config`, and `plugin_free_config`. Supported keywords are `server`, `port`, `timeout`, `user`, `password`, and `q_depth`.

Control flow: loader resets defaults, opens the provided file, verifies root ownership, exact 0640-style permissions, and regular-file status, parses whitespace-delimited `name = value`, dispatches keyword parsers, records basename as config name, then runs sanity checks for required server/user/password and nonzero timeout.

State and persistence: heap-owned strings are stored in `plugin_conf_t` and freed by `plugin_free_config`. Config values are process-local after load.

Dependencies and integration: used by the zOS plugin main path and `zos-remote-ldap.c`. Logging goes through `zos-remote-log.c`.

Risks: `port` is not range-checked; `server`, `user`, and `password` are unquoted single tokens only. Permission check requires the root read/write and group read bits but does not explicitly reject all extra bits as the comment suggests.

Test signals: tests should cover missing file, bad owner/mode/type, required-field failures, q_depth range, zero timeout, and token parse errors.
