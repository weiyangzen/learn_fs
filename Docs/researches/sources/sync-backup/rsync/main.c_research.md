# sources/sync-backup/rsync/main.c

## Purpose
`main.c` owns rsync process startup, command-line role selection, local and remote connection setup, client/server transfer orchestration, receiver/generator forking, summary statistics, daemon handoff, batch mode setup, and signal handling.

## Important APIs, Types, and Functions
Key functions are `main()`, `start_client()`, `client_run()`, `start_server()`, `child_main()`, `do_server_sender()`, `do_server_recv()`, `do_recv()`, `do_cmd()`, `get_local_name()`, `check_alt_basis_dirs()`, `handle_stats()`, `output_summary()`, `write_del_stats()`, `read_del_stats()`, `wait_process()`, `wait_process_with_flush()`, `shell_exec()`, and signal handlers such as `sigusr1_handler()`, `sigusr2_handler()`, and `remember_children()`.

## Control Flow
`main()` installs early signal handlers, records uid/gid and umask, sanitizes selected environment variables, resets daemon defaults, parses options, sets batch files, and dispatches to daemon, server, or client mode. `start_client()` interprets hostspecs to decide local copy, remote-shell transfer, daemon-over-shell, or socket daemon transfer, validates remote argument consistency, starts the connection, and calls `client_run()`. `client_run()` negotiates protocol, sends or receives file lists depending on `am_sender`, starts batch IO if needed, transfers files, waits for children, and outputs summaries. Server mode enters `start_server()`, which then calls sender or receiver routines. `do_recv()` forks a receiver child and leaves the parent as generator, splitting protocol streams and coordinating final goodbye messages.

## State and Persistence
The file manages process-global role flags (`am_sender`, `am_receiver`, `am_generator`, `local_server`, `daemon_connection`), pid status caching, start/end times, batch descriptors, cooked/raw argv, uid/gid state, and stats. Persistent effects include directory creation for destinations, file transfers through downstream modules, batch files, and possible privilege changes through `--copy-as`.

## Dependencies and Integration Points
This file integrates nearly all major rsync subsystems: options, daemon config, socket and remote-shell setup, file-list send/receive, filters, IO multiplexing, generator, receiver, sender, batch mode, hard links, logging, progress, and cleanup. It depends on popt, signal APIs, process management, filesystem calls, and platform locale support.

## Risks
The highest-risk areas are process-role transitions, descriptor ownership during receiver/generator split, remote argument validation, destination path decisions, and signal/child-status races. `do_cmd()` contains shell-like parsing for `RSYNC_RSH`; quoting bugs affect remote execution. `get_local_name()` must correctly handle single-file versus directory transfers, dry-run `--mkpath`, daemon filters, and trailing slashes. Signal handlers use restricted cleanup paths and can affect final exit codes.

## Test Signals
Test coverage should include local copy, remote source, remote destination, daemon socket, daemon-over-ssh, `--files-from`, `--read-batch`, `--write-batch`, `--copy-as`, dry-run with `--mkpath`, alternate basis directories, empty source/destination args, multiple remote source validation, receiver/generator shutdown, SIGUSR2 summary behavior, and stats output at multiple verbosity levels.
