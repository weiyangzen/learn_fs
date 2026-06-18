# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/619

## Purpose
This negative fixture is similar to report 618 but uses the newer text saying the `mand` mount option has been deprecated and ignored.

## Important APIs, types, and functions
No crash APIs are present. The relevant strings are IPv6 link readiness messages and the multi-line deprecation notice for `mand`.

## Control flow
The log shows network interfaces becoming ready around a mount-option deprecation warning. There is no stack trace, BUG line, panic, or report title.

## State and persistence behavior
It is static ignored console output. The lack of `TITLE` metadata persists the expected no-report state.

## Dependencies and integration points
It verifies parser integration with the warning suppression/ignore list for kernel informational notices.

## Risks and test signals
A parser regression could turn the deprecation block into a fake warning report. The correct test signal is that no report is extracted.
