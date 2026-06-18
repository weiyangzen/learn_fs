# sources/user-network-fs/samba/source4/dsdb/ft_scanner/ft_scanner_periodic.c

## Purpose

`ft_scanner_periodic.c` provides the periodic scheduler for the forest trust scanner task. It controls when the scanner runs and ensures only the current PDC emulator performs trust scanning.

## Important APIs, Types, and Functions

- `ft_scanner_periodic_schedule()` schedules or reschedules the next tevent timer for a `struct ft_scanner_service`.
- `ft_scanner_periodic_handler_te()` is the timer callback; it clears the current timer, runs the scanner, then schedules the next regular interval.
- `ft_scanner_periodic_run()` checks whether the local DC is the current PDC and invokes `ft_scanner_check_trusts()`.

## Control Flow

Scheduling clamps a zero interval to one second to avoid tight loops, computes `timeval_current_ofs(next_interval, 50)`, and compares it with any already scheduled timestamp. If an existing event is earlier than the proposed one, no reschedule occurs. Otherwise, it creates a new tevent timer, logs the scheduled time, frees the old timer, and stores the new timer.

When the timer fires, the handler clears `service->periodic.te`, runs the scanner, and schedules the next run using `service->periodic.interval`. If scheduling fails, it terminates the task. The run function uses `samdb_is_pdc()` to avoid multi-DC writers. Non-PDC DCs log a no-op. The PDC calls `ft_scanner_check_trusts()` and logs warnings on failure; it does not terminate the task for scan errors.

## State and Persistence Behavior

This file owns only in-memory timer state: `periodic.interval`, `periodic.next_event`, and `periodic.te`. It does not write samdb itself. Persistence occurs indirectly through `ft_scanner_check_trusts()` in `ft_scanner_tdos.c`.

## Dependencies and Integration Points

It depends on `struct ft_scanner_service` from `ft_scanner_service.h`, samdb PDC-role detection, tevent timers, task termination, and the scanner entry point declared through `ft_scanner_service_proto.h`.

## Risks

The scheduler intentionally avoids delaying an already earlier event, which is important if callers request an immediate or startup scan. Incorrect PDC detection would either suppress scanning or cause multiple DCs to race on trust blob updates. The 50 microsecond offset is small and mostly prevents exact-now scheduling edge cases; tests should avoid depending on exact timestamps.

## Test Signals

Tests should cover zero interval clamping, no-op reschedule when an earlier timer exists, replacement when a sooner timer is requested, PDC-only scanner invocation, non-fatal scan failure, and task termination on timer allocation/reschedule failure.
