# sources/user-network-fs/samba/source3/libsmb/libsmb_printjob.c

Purpose: implements printer-share helpers for opening print jobs, copying a remote file to a printer queue, listing jobs, and deleting jobs.

Important APIs: `SMBC_open_print_job_ctx()` validates context/path and delegates to the normal open function with `O_WRONLY`. `SMBC_print_file_ctx()` opens a source file from one context and a print job from another, copies 4096-byte chunks via configured read/write callbacks, closes both handles, and returns total bytes copied. `SMBC_list_print_jobs_ctx()` connects to the target share and calls `cli_print_queue()`. `SMBC_unlink_print_job_ctx()` connects and calls `cli_printjob_del()`.

Control flow/state: these operations do not keep extra persistent state beyond normal open `SMBCFILE` and server cache state. URL parsing and default-user fallback mirror file/directory operations. Error handling preserves `errno` around cleanup when opening or writing fails.

Dependencies and integration: depends on `SMBC_parse_path`, `SMBC_server`, context callback getters, and lower-level print `cli_*` calls. The compatibility API in `libsmb_compat.c` delegates to these through function pointers installed by `smbc_new_context()`.

Risks: `SMBC_open_print_job_ctx()` parses but does not otherwise use parsed path components before delegating to normal open; printer semantics rely on server/share behavior. `SMBC_print_file_ctx()` requires both contexts initialized and can leave the caller with only byte count, not detailed partial-write metadata. The condition `if (!fname && !printq)` rejects only both-null, so a single null may reach callback code. Test signals: source open failure, print job open failure with source close, write failure cleanup, byte count for multi-chunk copy, list callback invocation, delete status mapping, and null-argument validation.
