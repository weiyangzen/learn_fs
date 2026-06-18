# sources/security-integrity/audit-userspace/auparse/auditd-config.c

Purpose: A reduced auditd configuration parser used by libauparse to discover user-space parsing settings, especially the audit log file path and end-of-event timeout.

Important APIs, types, and functions: Public functions are `aup_load_config()` and `aup_free_config()`. Internal helpers include `aup_clear_config()`, `get_line()`, `nv_split()`, `kw_lookup()`, `log_file_parser()`, and `eoe_timeout_parser()`. The parser recognizes `log_file` and `end_of_event_timeout` keywords through `keywords[]`.

Control flow: `aup_load_config()` initializes a `daemon_conf` with broad auditd defaults, opens `CONFIG_FILE` using `O_NOFOLLOW`, wraps it in a `FILE *`, reads non-too-long lines, tokenizes `name = value`, looks up recognized keywords, and dispatches parser functions. Missing config is nonfatal and leaves defaults. `log_file_parser()` validates directory length, directory existence, basename presence, and read-open access to the log file before replacing `config->log_file`. `eoe_timeout_parser()` requires all digits and converts with `strtoul()`. `aup_free_config()` frees the allocated log file path.

State and persistence: Produces an in-memory `daemon_conf`; no persistent writes. It reads `/etc/audit/auditd.conf` or whatever `CONFIG_FILE` expands to. Defaults include `/var/log/audit/audit.log` and `EOE_TIMEOUT`.

Dependencies and integration points: Used by `auparse.c` in `setup_log_file_array()` and `au_setup_userspace_configitems()`. Depends on common audit tokenization/logging helpers, POSIX file/dir APIs, and `internal.h` definitions for `daemon_conf`.

Risks and edge cases: Only two keywords are recognized; other auditd config settings are ignored after token validation. `O_NOFOLLOW` protects the config file open from symlink traversal but log file validation uses plain `open()`. The parser allows one extra token after value but rejects two, matching audit config option patterns. It logs errors through `audit_msg()` with auparse message mode, so silent/default behavior depends on that state.

Test signals: Indirectly tested when `auparse_init(AUSOURCE_LOGS)` discovers audit logs and when end-of-event timeout behavior is exercised. Dedicated tests should cover missing config, unreadable config, bad `log_file`, nonnumeric timeout, and overlong lines.
