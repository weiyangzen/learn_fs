<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/server.c -->
# sources/user-network-fs/samba/source4/samba/server.c

## Purpose

`server.c` is the main `samba` AD DC server binary. It parses daemon options, prepares runtime directories and databases, initializes process models and services, starts configured services, and runs the top-level event loop.

## Important APIs, Types, and Functions

`struct server_state` holds the top-level event context and binary name. Major helpers include `cleanup_tmp_files()`, `setup_signals()`, `server_stdin_handler()`, `max_runtime_handler()`, `handle_inplace_db_upgrade_check_and_update_fl()`, `prime_ldb_databases()`, `setup_parent_messaging()`, `samba_parent_shutdown()`, `samba_terminate()`, `show_build()`, `binary_smbd_main()`, and `main()`.

## Control Flow

`main()` initializes talloc and calls `binary_smbd_main()`. Startup initializes command-line parsing, handles daemon/interactive modes, sets signal masks, logs version info, daemonizes if requested, cleans tmp files, creates lock/pid directories, opens the pidfile, disables recursive winbind calls, initializes GENSEC, process models, services, tevent, log tracing, stdin EOF handling, max-runtime timer, signal handlers, and role validation. It primes SAM/privilege databases, refuses backup databases, registers parent messaging, creates a process-control pipe, and starts services through `server_service_startup()`. Then it signals daemon readiness and waits in `tevent_loop_wait()`.

## State and Persistence Behavior

Startup deletes Samba tmp files, creates pid/lock directories, writes a pidfile, may trigger DSDB reindexing and functional-level updates inside a transaction, opens persistent database contexts for reuse, and registers imessaging names. Runtime state hangs from `server_state`.

## Dependencies and Integration Points

The file integrates command-line/loadparm, daemon helpers, DSDB/SAMDB, secrets/schannel, winbind recursion guard, GENSEC, process-model and service registries, cluster server IDs, IRPC, tevent tracing, and `tfork` or pthread atfork handling.

## Risks and Edge Cases

Startup has many fatal exits; configuration mistakes around server role, missing smb.conf, backup databases, pid directories, schannel store, or process model names abort the daemon. `recursive_delete()` panics on unlink failure. Fork/atfork control-pipe handling differs by pthread support. In-place DB updates happen early and must remain transaction-safe.

## Test Signals

Integration tests should cover daemon, foreground, and interactive modes; role-check failure paths; backup database refusal; database reindex/functional-level path; service startup under different models; stdin EOF termination; `smbcontrol samba shutdown`; `SAMBA_TERMINATE`; max-runtime exit; and `--show-build`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/server.c -->
