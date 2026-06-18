## sources/security-integrity/audit-userspace/src/ausearch.c

Purpose: main program for `ausearch`. It parses search options, reads audit logs/stdin/input files, assembles events, filters them, outputs matches, and manages checkpoints.

Important APIs/functions: `main()` coordinates lifecycle; `process_logs()` locates log files and checkpoint start positions; `process_file()`, `process_stdin()`, and `process_log_fd()` read events; `get_next_event()` feeds lines to the `lol` assembler with pipe timeout support; `chkpt_output_decision()` decides when checkpointed output may resume.

Control flow: after `check_params()`, it loads auditd config, sets EOE timeout, loads checkpoint data if requested, creates the assembler, chooses input source, processes complete events through `match()` and `output_event()`, updates last checkpoint event, saves checkpoint if clean, and frees lookup/parser/output state. Rotated logs are processed oldest-needed to newest by numeric suffix countdown.

State/persistence: process state includes `log_fd`, `lol lo`, `found`, `input_is_pipe`, timeout interval, `files_to_process`, auditd `config`, checkpoint flags, `userfile_is_dir`, and CLI globals. Persistence occurs only through checkpoint files via `ausearch-checkpt.c`.

Dependencies/integration: integrates `ausearch-options`, `ausearch-lol`, `ausearch-match`, `ausearch-report`, `ausearch-checkpt`, `ausearch-parse` log enumeration, `auditd-config`, `libaudit`, and `auparse`.

Risks/test signals: checkpoint correctness is subtle around inode reuse, partial events, `--start checkpoint`, and last-file flushing. `get_next_event()` uses SIGALRM to break pipe reads and shares static assembler ready state. Tests should cover no matches exit status, raw no-match silence, `--just-one`, stdin without checkpoint save, forced logs while stdin is pipe, directory input, rotated logs with checkpoint, corrupted checkpoint detection, EINTR/EOF handling, and cleanup paths.
