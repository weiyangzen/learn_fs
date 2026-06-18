# sources/security-integrity/audit-userspace/contrib/libauplugin/auplugin-example.c

Purpose: C example showing how to implement an audit dispatcher plugin with `libauplugin`, delegating stdin queueing and event feeding to the helper library while using `libauparse` callbacks for event inspection.

Important APIs and functions: Uses `auplugin_init`, `auplugin_event_feed`, `auplugin_stop`, `auparse_goto_record_num`, `auparse_get_type`, `auparse_get_record_text`, `auparse_get_num_fields`, `auparse_get_timestamp`, `auparse_first_record`, `auparse_next_record`, `auparse_first_field`, `auparse_next_field`, and `audit_msg_type_to_name`. Local functions are `term_handler`, `hup_handler`, `reload_config`, `dump_whole_event`, `dump_whole_record`, `dump_fields_of_record`, and callback `handle_event`.

Control flow: `main` installs SIGHUP and SIGTERM handlers, initializes `libauplugin` on stdin fd 0 with a 128-event in-memory queue, then starts `auplugin_event_feed` with a one-second timer. `term_handler` only honors SIGTERM from the parent process and calls `auplugin_stop` so the feed loop exits. `handle_event` reloads config when requested and iterates all records in a completed event; it prints AVC fields, syscall records, and whole MAC status events.

State and persistence: Uses process globals `stop` and `hup` as signal state. The queue is in memory only. Output is demonstration stdout text; real plugins would normally write elsewhere because stdout is often `/dev/null` under auditd.

Dependencies and integration: Includes `<auplugin.h>` and expects auditd/audisp plugin stdin framing. It is functionally comparable to `contrib/plugin/audisp-example.c` but moves manual select/feed logic into `libauplugin`.

Risks: It is an example, so processing is synchronous and prints records directly. The callback does not check `cb_event_type`, so it assumes `auplugin_event_feed` calls it only for complete events or that non-ready callbacks are harmless. Parent-only SIGTERM handling avoids arbitrary termination but can surprise manual testing.

Test signals: Build via the contrib Makefile, feed `ausearch --raw` output, send SIGHUP to exercise reload state, send SIGTERM from the parent/dispatcher path, and verify stdout for `AUDIT_AVC`, `AUDIT_SYSCALL`, and `AUDIT_MAC_STATUS`.
