# sources/user-network-fs/samba/source3/printing/print_generic.c

Purpose: implements command-based printing for generic/non-CUPS backends using configured shell commands for submit, queue listing, job control, and queue control.

Important APIs and functions: `print_run_command()` substitutes local tokens and loadparm variables, optionally applies advanced service/user substitution, then runs the command through `smbrun_no_sanitize()`. `generic_queue_get()` executes an `lpq` command and parses output with `parse_lpq_entry()`. `generic_job_submit()` changes into the spool directory, sanitizes `%J` job-name substitution with `replace_print_cmd_J()`, runs the print command, then re-queries the queue to map Samba job IDs to backend `sysjob` IDs. `generic_job_delete()`, `generic_job_pause()`, `generic_job_resume()`, `generic_queue_pause()`, and `generic_queue_resume()` call configured commands. `generic_printif` exports the backend vtable.

Control flow: submit extracts the spool directory and filename, picks a default job name if absent, detects mixed quoting for `%J`, substitutes `%s/%f/%z/%c`, runs the backend, and restores the original working directory even on failure. Queue parsing allocates one entry per output line and keeps entries accepted by the parser.

State and persistence: relies on external spooler commands for real state. It mutates `pjob->sysjob` and may track jobs as Unix jobs if backend ID lookup fails. No durable state is stored directly here.

Dependencies and integration: depends on smb.conf print commands, substitution helpers, current user info, `smbrun_no_sanitize()`, `fd_lines_load()`, and printing parser/type definitions.

Risks: command execution is inherently sensitive. The `%J` sanitization and CVE-2026-4480 mixed-quoting fallback are key security controls. `chdir()` process-wide state is dangerous if used in a multithreaded context. Tests should cover missing commands, substitution tokens, `%J` unsafe characters, mixed quoting warning/fallback, queue parse matching, directory restoration, and configured command failures.
