# sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-config.h

Purpose: declares z/OS remote plugin configuration structure and lifecycle functions.

Important APIs and data: `plugin_conf_t` includes config filename, server, port, user, password, timeout, queue depth, and a counter. Declares clear/load/free functions.

Control flow: no implementation; loaded values drive plugin startup and LDAP session initialization.

State and persistence: holds process-local config with heap-owned string fields.

Dependencies and integration: consumed by the zOS remote plugin and LDAP wrapper.

Risks: password is stored in process memory as plain text. `counter` is not reset by clear according to implementation comment, so callers need to understand its lifecycle.

Test signals: parser and plugin startup tests validating field propagation.
