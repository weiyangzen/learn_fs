<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-clock.c -->
# sources/test-tools/stress-ng/stress-clock.c

## Purpose
Implements the `clock` stressor, broadly exercising POSIX clock, timer, nanosleep, adjtime, and Linux PTP clock-id paths, including expected invalid argument and permission failures.

## Important APIs, Types, and Functions
`stress_clock_info` registers the stressor when librt and clock APIs are available. `stress_clock_info_t` maps clock ids to names. Tables list clocks for `clock_gettime`/`clock_getres`, `clock_nanosleep`, and `timer_create`. Helpers include `stress_clock_name()`, `check_invalid_clock_id()`, `aux_clock_nonfatal_error()`, and `FD_TO_CLOCKID()`.

## Control Flow
`stress_clock()` seeds the random generator deterministically, synchronizes, then loops through thread CPU clock reads/set probes, invalid clock ids, getres/gettime for each known clock, invalid and permission-sensitive `clock_settime`, periodic invalid `clock_nanosleep`, `clock_adjtime` probes, POSIX timer create/set/get/delete cycles, and optional `/dev/ptp0` file-clock reads. Verification mode reports unexpected errors while known unsupported or permission-denied cases are tolerated.

## State and Persistence Behavior
No persistent state is written. The stressor creates short-lived POSIX timers and opens `/dev/ptp0` if present. It avoids repeatedly setting invalid time after one successful invalid-timespec probe to limit time drift risk.

## Dependencies and Integration Points
Uses stress-ng clock shims, capability checks, deterministic random utilities, optional poll/timex headers, POSIX timers, Linux file-descriptor clock ids, process-state reporting, and bogo accounting. It is `VERIFY_OPTIONAL` because platform clock behavior varies.

## Risks and Edge Cases
Clock availability varies by kernel and libc. Some clocks reject settime by design; unprivileged users should receive EPERM or EINVAL. Auxiliary clocks may be disabled. Timer creation can fail due to limits. Interacting with realtime clock APIs as root could affect system time if invalid-guard logic is wrong.

## Test Signals
Expected signals are sustained bogo operations, no unexpected verification failures, successful handling of unavailable clocks, and timer resources deleted each loop. Tests should include verify and non-verify modes and a system without `/dev/ptp0`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-clock.c -->
