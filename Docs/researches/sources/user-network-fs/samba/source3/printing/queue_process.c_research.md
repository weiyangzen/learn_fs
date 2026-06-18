# sources/user-network-fs/samba/source3/printing/queue_process.c

## Purpose

`queue_process.c` starts and manages the background print queue daemon (`samba-bgqd`) and registers its messaging handlers. It isolates expensive pcap reloads, print queue refreshes, stale printer removal, and driver upgrade work from client-serving smbd processes.

## Important APIs, Types, and Functions

- `delete_and_reload_printers_full()` reconciles smb.conf/printer-list state into NT printer registry entries and removes stale autoloaded printers.
- `reload_pcap_change_notify()` reloads printers in the background process and broadcasts `MSG_PRINTER_PCAP`.
- `struct bq_state` keeps tevent, messaging, idle housekeeping, and signal handler state.
- `printing_subsystem_queue_tasks()` schedules printcap housekeeping based on `lp_printcap_cache_time()` and `lp_load_printers()`.
- `register_printing_bq_handlers()` registers `MSG_SMB_CONF_UPDATED`, `MSG_PRINTER_UPDATE`, `MSG_PRINTER_DRVUPGRADE`, signal handlers, loads shares, reloads pcap cache, and schedules housekeeping.
- `start_background_queue()` spawns `samba-bgqd` with ready/watch file descriptors and waits for readiness.
- `printing_subsystem_init()` starts the background daemon and initializes the print backend.
- `send_to_bgqd()` looks up the daemon PID file and sends a message to it.

## Control Flow

Initialization calls `start_background_queue()`, which creates a readiness pipe, builds argv for `samba-bgqd`, spawns it with inherited environment, closes the write end in the parent, and waits to read the daemon PID. After the daemon is available, `print_backend_init()` prepares per-printer TDBs and NT printing.

Inside the daemon, `register_printing_bq_handlers()` registers message handlers for configuration updates, queue-update messages, and driver upgrades. It also installs SIGHUP and SIGCHLD handlers, loads shares for `[printers]`, immediately reloads the pcap cache, and schedules periodic housekeeping. Housekeeping calls `pcap_cache_reload()` with a callback that does full printer reconciliation before notifying smbd processes.

`send_to_bgqd()` is the client-side send path. It reads the `samba-bgqd` PID file and sends `msg_type` and buffer to that process over Samba messaging.

## State and Persistence

`bq_state` is in-memory daemon state. Persistent daemon identity is the `samba-bgqd` PID file. Printer state is not stored here directly; reconciliation updates NT printing/registry state through helper calls and queue updates are performed by handlers in `printing.c`.

## Dependencies and Integration Points

The file depends on tevent, Samba messaging, loadparm, pcap/printer-list APIs, NT printing functions, spoolss driver upgrade handlers, auth system-session creation, locking, pidfile utilities, `posix_spawn()`, and `samba-bgqd`. It is used by smbd startup and by printing queue refresh callers.

## Risks and Edge Cases

- `delete_and_reload_printers_full()` can permanently remove printer and driver registry entries, so it must only be called after a successful pcap reload.
- Failure to start or signal `samba-bgqd` disables normal background refresh and may force local updates elsewhere.
- Signal handlers reload configuration and pcap state while daemon work is live, so handler registration/destruction must be consistent.
- `bq_sig_chld_handler()` inspects `status` after `waitpid`; callers should ensure abnormal child handling remains robust.

## Test Signals

Tests should verify daemon spawn readiness, lost/duplicate daemon PID handling, message registration and deregistration, SIGHUP reload behavior, housekeeping scheduling disabled/enabled cases, `MSG_SMB_CONF_UPDATED` reload, and `send_to_bgqd()` behavior when the PID file is absent.
