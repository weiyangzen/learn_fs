# sources/security-integrity/audit-userspace/src/auditd-event.c

## Purpose
`auditd-event.c` handles audit event formatting, local log writes, disk space/size actions, log rotation, network acknowledgements, and the bridge into live reconfiguration.

## Important APIs, Types, And Functions
Public APIs include `dispatch_network_events`, `write_logging_state`, `shutdown_events`, `init_event`, `auditd_get_exec_pid`, `auditd_clear_exec_pid`, `resume_logging`, `cleanup_event`, `format_event`, `enqueue_event`, `create_event`, and `handle_event`. Internal hotspots include `format_raw`, `format_enrich`, `write_to_log`, `check_log_file_size`, `check_space_left`, `do_space_left_action`, `do_disk_full_action`, `do_disk_error_action`, `rotate_logs`, `shift_logs`, `open_audit_log`, `safe_exec`, and `reconfigure`.

## Control Flow
`init_event` stores the config, opens stdout or the audit log, applies disk permissions, checks rotation state, allocates the format buffer, and starts an async flush thread. Events are formatted raw/enriched, optionally written to local logs, flushed according to config, acknowledged to remote senders, and routed to disk/rotation/error handlers. `AUDIT_DAEMON_RECONFIG` events invoke `auditd_reconfigure` through a callback context.

## State And Persistence
The file holds global mutable logging state: config pointer, atomic log fd, `FILE *`, disk warning flags, suspension state, known rotated logs, helper child pid, format buffer, log size, flush thread primitives, and auparse state. It persists audit records to the configured log file, rotates files on size/space triggers, changes file ownership/modes, and can close logging until resumed.

## Dependencies And Integration
It depends on pthreads, signals, filesystem APIs, `libaudit`, `auparse`, `common.h`, `private.h`, `auditd-config.h`, and `auditd-reconfigure.h`. `auditd.c` supplies `stop`, `event_is_prealloc`, and `distribute_event`; `auditd-listen.c` uses `create_event` and ack callbacks for remote clients.

## Risks
Risks include global state races between the main loop and flush thread, ownership of `reply.message`, truncation in formatting, disk action side effects (`single`, `halt`, helper exec), reopen failures after rotation/reconfigure, and remote ack correctness when logging is suspended or disk-full. The weak `event_is_prealloc` fallback changes cleanup behavior depending on link target.

## Test Signals
`src/test/format_event_test.c` verifies raw/enriched formatting and interpretation separator behavior. Additional test signals should exercise write failure branches, async flush, rotation naming, suspended/resume paths, network ack types, and reconfigure callback behavior with mocked operations.
