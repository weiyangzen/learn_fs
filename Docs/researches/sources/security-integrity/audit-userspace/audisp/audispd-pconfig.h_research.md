## sources/security-integrity/audit-userspace/audisp/audispd-pconfig.h

Purpose: plugin configuration model for audisp dispatcher.

It defines active/type/format enums and `plugin_conf_t` fields for executable path, argv array, format, socketpair fds, child pid, inode, reload checked flag, config name, and restart count. Lifecycle APIs are `clear_pconfig`, `load_pconfig`, and `free_pconfig`. State is runtime-owned by dispatcher list nodes. Dependencies are libaudit types and attribute macros. Risks include ownership of `const char *path` despite allocation/free, pipe fd lifecycle, and restart counter preservation across reloads. Tests should validate clear/free idempotence and reload replacement.
