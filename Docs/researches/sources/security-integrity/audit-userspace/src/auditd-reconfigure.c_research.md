# sources/security-integrity/audit-userspace/src/auditd-reconfigure.c

## Purpose
`auditd-reconfigure.c` applies a loaded `daemon_conf` to a running daemon. It was separated from `auditd-event.c` and uses a context object to update logging state via explicit callbacks.

## Important APIs, Types, And Functions
Public API is `auditd_reconfigure`. Internal phases are `reconfigure_general_options`, `reconfigure_network_options`, `reconfigure_dispatcher_options`, `reopen_log_file`, `reconfigure_log_file_options`, `reconfigure_disk_space_options`, and `emit_reconfigure_event`.

## Control Flow
`auditd_reconfigure` logs requester identity, then applies changes from least to most invasive: general daemon options, network listener options, dispatcher/plugin options, log file/rotation options, disk space thresholds/actions, dispatcher reconfigure, and final success event emission. Log changes set flags for reopen, size check, or space check; `reopen_log_file` uses callbacks supplied by `auditd-event.c`.

## State And Persistence
It mutates the live `daemon_conf`, transfers or frees string fields from the new config, resets disk warning flags, may reopen persistent log files, recalculates percentage thresholds against the current log fd, restarts/reconfigures listener pieces, and emits a final `AUDIT_DAEMON_CONFIG` record.

## Dependencies And Integration
It depends on `auditd-reconfigure.h`, `auditd-dispatch.h`, `auditd-listen.h`, and `private.h`, plus external `update_report_timer`. The context is built in `auditd-event.c` and the event originates from `auditd-reconfig.c`.

## Risks
String ownership is subtle: some nconf pointers are transferred into oconf, some are duplicated, some freed, and some can alias after listener reconfigure. Null handling is incomplete in comparisons like `strcmp(oconf->action_mail_acct, nconf->action_mail_acct)` if future defaults change. Reopen/space checks can suspend logging. Random sequence generation for the emitted event is not security-critical but non-deterministic.

## Test Signals
No focused reconfigure unit test is present. The linked `format_event_test` includes this file for integration. Valuable tests would use a fake context and callbacks to verify ownership, reopen flags, size/space check ordering, listener restart decisions, and emitted event contents.
