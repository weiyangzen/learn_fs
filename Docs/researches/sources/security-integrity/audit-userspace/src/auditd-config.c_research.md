# sources/security-integrity/audit-userspace/src/auditd-config.c

## Purpose
`auditd-config.c` owns `auditd.conf` loading, default initialization, validation, and cleanup for `struct daemon_conf`. It is a table-driven parser: `keywords[]` maps config names to small parser functions, while value tables map strings to enum values for log formats, flush techniques, failure actions, size actions, node name formats, yes/no values, overflow actions, and transports.

## Important APIs, Types, And Functions
Public entry points are `set_allow_links`, `set_config_dir`, `clear_config`, `load_config`, `audit_lookup_format`, `create_log_file`, `resolve_node`, `setup_percentages`, `free_config`, and `failure_action_to_str`. Internal helpers include `get_line`, `nv_split`, `kw_lookup`, `replace_string`, `check_exe_name`, `validate_email`, parser functions for every keyword, `calc_percent`, and `sanity_check`.

## Control Flow
`load_config` calls `clear_config`, chooses the config path, opens it with `O_NOFOLLOW` unless links are allowed, checks root ownership/world writability/regular-file status, then reads line by line. Each line is tokenized as `name = value [option]`, looked up in `keywords[]`, checked for option allowance, and dispatched to the keyword parser. Parsers validate ranges, file properties, executable paths, optional compile-time listener/GSS support, and string allocations. A non-empty file ends with `sanity_check`.

## State And Persistence
The file mutates the passed `daemon_conf` and module globals `allow_links`, `config_dir`, `config_file`, and `log_test`. Defaults include `/var/log/audit/audit.log`, `/etc/audit/plugins.d`, enriched logging, root mail, queue depth 2000, TCP disabled, and end-of-event timeout `EOE_TIMEOUT`. `free_config` releases string fields and resets config path globals. `create_log_file` persists a new audit log with owner-only write and group-readable mode under a restrictive umask.

## Dependencies And Integration
It depends on libc, filesystem/stat APIs, name service APIs, `libaudit`, `private.h`, and `common.h`. Runtime consumers are `auditd.c`, `auditd-event.c`, `auditd-listen.c`, `auditd-dispatch.c`, and `auditd-reconfigure.c`. Compile-time flags gate listener and GSS parsing behavior.

## Risks
Most parser branches are security-sensitive because they accept filesystem paths, email addresses, helper executables, and network parameters. Important risks are ownership/permission bypasses, path replacement during validation/open, allocation failure preserving old state, stale string ownership during live reconfiguration, percent threshold calculations on unusual filesystems, and DNS dependency in `validate_email` / `resolve_node`.

## Test Signals
`src/test/auditd_config_alloc_test.c` directly includes this file and tests allocation-failure preservation for `name_parser`, `log_file_parser`, and `set_config_dir`. Additional useful tests would cover malformed tokenization, executable permission matrices, percent thresholds, listener-disabled parsing, and `sanity_check` failures.
