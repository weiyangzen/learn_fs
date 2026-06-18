# File Research: sources/local-fs/dlm/dlm_controld/main.c

This is the main executable entry point and event loop for `dlm_controld`. It initializes options, logging, Corosync, configfs, kernel DLM monitoring, uevent handling, client sockets, query sockets, plocks, and optional helper-process command execution.

Major areas:
- Client/poll management: dynamic arrays of `struct client` and `struct pollfd`, with `client_add`, `client_dead`, `client_ignore`, and `client_back`.
- I/O helpers: daemon-local `do_read()` and `do_write()`.
- Helper process: `setup_helper()` forks `run_helper()`, uses nonblocking pipes, receives `DLM_MSG_RUN_REPLY`, sends run requests/cancels, and tracks helper heartbeats.
- Run operations: `start_run_operation()`, `find_run()`, `check_run_operation()`, and `clear_run()` maintain cluster-wide helper command state and result counts.
- Lockspace creation and lookup: `create_ls()`, `find_ls()`, and `find_ls_id()`.
- Filesystem registration: tracks fs-controlled lockspaces via an internal `fs_register_list`.
- Kernel uevents: `setup_uevent()` opens `NETLINK_KOBJECT_UEVENT`; `process_uevent()` handles DLM `online` and `offline` events by joining/leaving lockspaces.
- Query thread: `process_queries()` listens on `DLMC_QUERY_SOCK_PATH`, validates headers, locks `query_mutex`, and serves dump/status/lockspace/node requests.
- Control socket: `process_listener()` and `process_connection()` handle `DLMC_SOCK_PATH` commands such as fs register/notified, run start/check, reload config, and dynamic set config.
- Main loop: `loop()` initializes subsystems in order, enters `poll()`, dispatches fds, processes deferred fencing/lockspace/plock work, and tears down on exit.
- Option handling: `set_opt_defaults()`, `set_opt_cli()`, `get_ind_name()`, `get_ind_letter()`, `get_dlm_option()`, and `print_usage()`.
- Process singleton: `lockfile()` creates runtime dirs, takes an fcntl write lock, writes pid, and `unlink_lockfile()` cleans up.

Startup order in `loop()`:
1. Start query thread and control listener.
2. Connect Corosync cfg.
3. Check uncontrolled kernel lockspaces.
4. Unfence local node.
5. Load node config and quorum cluster service.
6. Discover misc devices and configure configfs.
7. Set up monitor fd, configfs members, uevent socket, daemon CPG, protocol, plocks, and optional helper fd.
8. Notify systemd if enabled.
9. Allow fencing only after protocol setup.

Important interactions:
- `member.c` supplies Corosync cfg/quorum setup and cluster membership callbacks.
- `plock.c` supplies `/dev/misc/dlm_plock` handling and state dump.
- `logging.c` supplies debug/config/plock dump buffers.
- `action.c`/other daemon modules outside this group supply configfs/kernel operations, CPG, fencing, and lockspace transition logic.
- `lib.c` is coupled to command handling and query reply layouts here.

Notable details:
- Query serving is moved to a separate thread because the main thread may block on sysfs writes.
- `query_mutex` serializes query snapshots against main-loop state changes.
- Shutdown is ignored if active lockspaces remain after SIGTERM/SIGINT.
- `process_connection()` validates magic and major protocol version, but command-specific extra payload sizes rely on command logic.
- The option parser supports long options, short options, boolean shorthand, bundled boolean letters, `--name=value`, and environment override `DLM_CONTROLD_DEBUG`.
