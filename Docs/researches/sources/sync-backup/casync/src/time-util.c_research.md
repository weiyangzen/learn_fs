# sources/sync-backup/casync/src/time-util.c

Purpose: implements time conversion/formatting helpers for monotonic and realtime values.

Important APIs/types/functions: includes functions for formatting timestamps or durations and for conversions used by polling timeouts. It complements inline conversions in `time-util.h`.

Control flow/state: stateless helpers convert between numeric nanoseconds and calendar/`timespec` representations, generally returning negative errno on invalid input or formatting failure.

Dependencies/integration: used by notify-wait timeout handling, progress/reporting paths, and utility code that needs monotonic deadline arithmetic.

Risks/test signals: overflow and clock-domain mixups are the main risks. `notify-wait.c` exercises `now`/`nsec_to_timespec` in a 30-second readiness timeout path.

Source research group: `subset-b-009122`.
