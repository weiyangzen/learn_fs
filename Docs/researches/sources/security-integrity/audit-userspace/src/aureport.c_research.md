## sources/security-integrity/audit-userspace/src/aureport.c

Purpose: main program for `aureport`. It parses report options, locates audit logs or stdin/input files, assembles records into complete audit events, runs report scanning, and prints titles/wrap-up output.

Important APIs/functions: `main()` owns setup and teardown; `process_logs()` enumerates rotated logs using `audit_log_list()` and `audit_log_find_start()`; `process_file()` and `process_stdin()` set `log_fd`; `process_log_fd()` loops over events; `get_event()` feeds raw lines to `lol_add_record()` and pulls ready `llist` events; `process_event()` calls `scan()` and `per_event_processing()`.

Control flow: after `check_params()`, it raises file/cpu limits, loads auditd config, applies `end_of_event_timeout`, initializes `auparse`, counters, and the list-of-lists event assembler. It chooses directory, regular file, stdin pipe, forced logs, or configured logs. For each complete event in time range it scans and accumulates or emits. On EOF of the last file, `terminate_all_events()` flushes incomplete events.

State/persistence: process state includes `log_fd`, `lol lo`, `found`, `files_to_process`, `very_first_event`, `very_last_event`, `config`, and a static `auparse_state_t *au`. No persistent writes. It frees counters, lookup caches, config, and `user_file`.

Dependencies/integration: integrates `aureport-options`, `aureport-scan`, `ausearch-lol`, `ausearch-parse` log enumeration, `auditd-config`, `libaudit`, and internal `auparse` interpretation helpers.

Risks/test signals: rotated log traversal depends on first timestamps and descending numeric suffixes. Error handling around `auparse_init()` and config fallback should be covered. Tests should exercise stdin, directory input, missing logs, time range skipping, last-file incomplete event flushing, and report type `RPT_TIME`.
