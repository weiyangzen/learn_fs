<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_out_push.c -->
# sources/user-network-fs/samba/source4/wrepl_server/wrepl_out_push.c

## Purpose

This file schedules and supervises outbound WREPL push notifications to configured push partners when local WINS version changes exceed a configured threshold.

## Important APIs, Types, and Functions

- `wreplsrv_out_partner_push()` starts one push notification for a partner.
- `wreplsrv_push_handler_creq()` handles completion, one retry, error counting, and cleanup.
- `wreplsrv_calc_change_count()` tracks per-partner maxVersion deltas with overflow protection.
- `wreplsrv_out_push_run()` scans partners and starts eligible push notifications.

## Control Flow

`wreplsrv_out_push_run()` reads the current max WINS DB version, iterates push partners, skips disabled push thresholds, calculates the version delta since the last check, and starts a push if the delta reaches the configured `change_count`. Each push uses `wreplsrv_push_notify_send()`, with inform/update selected from partner configuration. Completion resets error count on success; the first failure retries once, later failures give up until a later trigger.

## State and Persistence Behavior

The file updates `partner->push.maxVersionID`, `creq`, `notify_io`, `last_status`, and `error_count`. It does not directly persist WINS records; it reacts to persistent WINS DB version changes and notifies peers.

## Dependencies and Integration Points

It depends on `winsdb_get_maxVersion()`, outbound push notify helpers, WREPL partner configuration, and periodic scheduling through `wrepl_periodic.c`.

## Risks and Edge Cases

`wreplsrv_calc_change_count()` updates `maxVersionID` even when the threshold is not reached, so it measures changes since the last scan, not since the last successful push. A running push suppresses additional push attempts. Repeated failures are only retried once immediately.

## Test Signals

Signals include push notifications when version deltas cross thresholds, no notification below threshold, no duplicate in-progress notifications, one retry after a failure, and reset error count after success.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_out_push.c -->
