# sources/security-integrity/audit-userspace/contrib/plugin/audisp-example.c

Purpose: Manual audit dispatcher plugin example using `libauparse` directly. It demonstrates stdin nonblocking reads, event aging, callback registration, signal handling, and basic record inspection.

Important APIs and functions: Uses `auparse_init(AUSOURCE_FEED)`, `auparse_set_eoe_timeout`, `auparse_add_callback`, `auparse_feed_has_data`, `auparse_feed_age_events`, `auparse_feed`, `auparse_flush_feed`, `auparse_destroy`, record/field iteration APIs, and `audit_msg_type_to_name`. Local functions mirror the libauplugin example: signal handlers, `reload_config`, `dump_whole_event`, `dump_whole_record`, `dump_fields_of_record`, and `handle_event`.

Control flow: `main` installs SIGHUP/SIGTERM handlers, sets stdin nonblocking, initializes auparse feed mode, and enters a loop. It waits indefinitely when no partial event exists, or waits one second when auparse has buffered data so aged events can be flushed. Read data is fed to auparse until EOF or a stop request. The callback ignores non-`AUPARSE_CB_EVENT_READY` notifications and branches on record types.

State and persistence: Globals `stop`, `hup`, and `au` hold runtime state. No durable state is stored. Demonstration output goes to stdout.

Dependencies and integration: Includes local `libaudit.h` and `auparse.h`; intended for auditd/audisp string format stdin. Comments warn that real plugins should add an internal queue to avoid backing up auditd and the kernel backlog.

Risks: This example manually manages nonblocking IO and event aging, so production copies can easily get queueing wrong. `stop` and `hup` are `volatile int` rather than `sig_atomic_t`. The read loop uses fixed `MAX_AUDIT_MESSAGE_LENGTH` buffers and stdout diagnostics unsuitable for daemon deployment.

Test signals: Build with the contrib Makefile, feed `ausearch --raw` output, test EOF flushing, timeout event aging, SIGHUP reload path, SIGTERM parent check, and callback output for AVC/syscall/MAC status records.
