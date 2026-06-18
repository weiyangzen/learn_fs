<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_out_pull.c -->
# sources/user-network-fs/samba/source4/wrepl_server/wrepl_out_pull.c

## Purpose

This file schedules and supervises outbound WREPL pull cycles for configured pull partners.

## Important APIs, Types, and Functions

- `wreplsrv_out_pull_reschedule()` sets `partner->pull.next_run` and requests a service periodic wakeup.
- `wreplsrv_pull_handler_creq()` handles pull-cycle completion, retry, backoff, and cleanup.
- `wreplsrv_out_partner_pull()` starts a pull cycle for a partner, optionally using an inform-supplied owner table.
- `wreplsrv_out_pull_run()` scans all partners and starts due pull cycles.

## Control Flow

`wreplsrv_out_pull_run()` iterates partners, skipping non-pull partners, disabled intervals, and partners whose next run has not expired. Due partners are immediately rescheduled for their normal interval and `wreplsrv_out_partner_pull()` is invoked. A partner with an in-progress pull is skipped. Completion resets error count on success. The first failure triggers an immediate retry using the old owner table; later failures schedule increasing retry intervals capped at the normal pull interval.

## State and Persistence Behavior

State is stored in `partner->pull`: `next_run`, `creq`, `cycle_io`, `last_status`, and `error_count`. Persistent WINS state is changed indirectly by the pull cycle's record application.

## Dependencies and Integration Points

It depends on `wreplsrv_pull_cycle_send/recv()`, service periodic scheduling, WREPL partner configuration, and `wrepl_table` data supplied by inbound inform messages.

## Risks and Edge Cases

If allocation fails, the pull request is logged and ignored. A stuck `partner->pull.creq` prevents new pulls. Retry uses the previous `cycle_io` owner array, so lifetime transfer must remain correct.

## Test Signals

Signals include due partner detection, no duplicate pulls while one is active, successful error reset after success, immediate first retry on failure, increasing retry schedule after repeated failures, and eventual WINS DB convergence after pull cycles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_out_pull.c -->
