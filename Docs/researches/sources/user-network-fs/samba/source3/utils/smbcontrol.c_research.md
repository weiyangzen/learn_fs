# sources/user-network-fs/samba/source3/utils/smbcontrol.c

`smbcontrol.c` implements Samba's administrative messaging utility. It sends typed internal messages to daemons or specific PIDs to control debug/profile state, reload configuration, trigger print notifications, force disconnects, manage winbind state, retrieve diagnostics, and run developer-only fault/sleep commands.

The core helpers are `send_message`, `wait_replies`, `parse_dest`, and `do_command`. Command handlers are registered in `msg_types[]` and share a common signature. Reply callbacks print PIDs, strings, counters, profile levels, ring buffer logs, and winbind validation results. Destination parsing supports `all`, `self`, numeric PIDs, pidfiles, and messaging names DB entries.

`main` initializes Samba command-line handling, parses timeout, creates the command-line messaging context and global event context, then dispatches. One-way commands validate arguments and send messages. Query commands register callbacks, send requests, wait until timeout or expected replies, and deregister. Some commands directly edit local state, notably winbind online/offline markers in `winbindd_cache.tdb`; optional stack tracing uses ptrace/libunwind.

Dependencies include Samba messaging, server-id DB, pidfiles, tevent, TDB, printing notification helpers, nmb packet code, loadparm, and optional libunwind. Risks include disruptive commands, global `num_replies`, a suspicious deregistration in `do_profilelevel`, and timeout-based broadcast completion. Test signals: destination resolution, usage errors, ping/debug/profile replies, winbind marker behavior, invalid IP rejection, developer gating, and help table consistency.
