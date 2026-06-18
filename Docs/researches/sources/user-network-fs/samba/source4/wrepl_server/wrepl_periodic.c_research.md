<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_periodic.c -->
# sources/user-network-fs/samba/source4/wrepl_server/wrepl_periodic.c

## Purpose

This file coordinates periodic WREPL maintenance. Each timer tick reloads partners, runs WINS scavenging, starts due pulls, and sends due push notifications.

## Important APIs, Types, and Functions

- `wreplsrv_periodic_run()` performs the ordered maintenance steps.
- `wreplsrv_periodic_handler_te()` handles tevent timer expiration.
- `wreplsrv_periodic_schedule()` schedules or reschedules the next timer.
- `wreplsrv_setup_periodic()` schedules the first tick.

## Control Flow

The timer callback clears the current timer pointer, schedules the next normal periodic tick, then calls `wreplsrv_periodic_run()`. Scheduling coerces zero intervals to one second, adds a 5000 microsecond offset, and avoids replacing an existing timer if the new requested time is later than the current next event. It frees the old timer only after creating the new one.

## State and Persistence Behavior

Timer state is held in `service->periodic.te` and `service->periodic.next_event`. Persistent WINS DB effects occur through called scavenging and replication functions.

## Dependencies and Integration Points

It depends on tevent timers, task service termination, partner loading, scavenging, outbound pull, and outbound push modules.

## Risks and Edge Cases

Because partner reload occurs before each maintenance pass, configuration/database errors can prevent scavenging and replication. A scheduling failure terminates the task. Maintenance errors are logged but do not stop future timer scheduling.

## Test Signals

Signals include initial timer creation, no tight loop on zero intervals, partner reload before replication, scavenging/pull/push invocation in order, and earlier reschedules replacing later timers when retries need quicker wakeups.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/wrepl_server/wrepl_periodic.c -->
