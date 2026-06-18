# sources/security-integrity/audit-userspace/src/auditctl.c

Purpose: command-line tool for controlling Linux audit: status, rule loading, rule listing/deletion, watches, backlog/failure settings, user messages, loginuid immutability, auditd signals, and rules-file processing.

Important APIs/functions: `main`, `setopt`, `handle_option`, option handlers `opt_*`, `fileopt`, `handle_request`, `get_reply`, `reset_vars`, `audit_rule_setup`, `audit_setup_watch_name`, `audit_setup_perms`, `check_rule_mismatch`, `send_signal`, `report_status`, and optional `parse_io_uring`.

Control flow: `main` validates arguments/root capability, chooses direct CLI or `-R` file load, initializes netlink/rule state, parses options with `getopt_long`, then sends requests or reads replies. `fileopt` opens a regular non-world-writable file, tokenizes lines with escaped-space preprocessing, resets parser globals per line, parses options, and handles each request. `handle_request` sends add/delete rule operations, defaulting missing non-task syscalls to `all`, retries legacy watch rules with `AUDIT_WATCH`, and closes the audit fd unless listing is still active.

State and persistence: process globals track fd, key buffer, add/delete/action state, ignore/continue behavior, interpretation mode, and `rule_new`. It also resets libaudit parser globals such as `_audit_elf` between rules. Kernel audit subsystem state is changed through netlink; rules-file changes persist only in the kernel until reboot/reload unless the file remains installed.

Dependencies and integration: depends on libaudit rule APIs, netlink transport, `auditctl-listing`, `delete_all_rules`, aucommon messaging, syscall table lookup, kernel feature macros, and optional pidfd syscalls for safer auditd signaling.

Risks and test signals: complex global state makes reset correctness critical for `-R` loads. Path validation rejects relative paths but only warns on `..` and wildcards. `process_key_option` enforces key length and separator restrictions. Version skew can make newer fields/syscalls fail unless `-i`/`-c` is used. Test with CLI status/list/add/delete, rules-file loading with comments/escapes/errors, watch rules, key filtering, immutable-mode handling, and auditd signal paths.
