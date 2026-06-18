# sources/security-integrity/audit-userspace/audisp/plugins/remote/remote-config.c

Purpose: parses and validates `audisp-remote.conf` into `remote_conf_t`.

Important APIs and data: exports `clear_config`, `load_config`, and `free_config`. Parser tables cover server, ports, transport, mode, queue file/depth, format, retry/heartbeat values, GSS options, failure actions, remote ending action, overflow action, and startup failure action.

Control flow: `load_config` sets defaults, verifies the config file is root-owned, regular, and not world-writable, then parses `name = value [option]` tokens. Parser callbacks convert enums, duplicate string fields, check absolute queue paths, validate executable action paths and permissions, and perform final sanity checks.

State and persistence: dynamically allocated strings are stored in the caller-owned config and freed by `free_config`. No state persists beyond config files and process memory.

Dependencies and integration: consumed by `audisp-remote.c`; optional GSS options compile differently under `USE_GSSAPI`. Exec failure actions require root-owned 0750 absolute executables.

Risks: tokenization is whitespace-only and does not support quoted values. `remote_server` is not required by sanity check despite being needed for connection. Some enum values exist in the header but are not accepted by parser tables.

Test signals: parser tests should cover defaults, permission failures, every enum value, exec option validation, queue_file absoluteness, GSS disabled behavior, and `mode=forward` with non-managed format.
