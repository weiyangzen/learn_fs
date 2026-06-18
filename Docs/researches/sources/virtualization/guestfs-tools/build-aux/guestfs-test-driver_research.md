# File Research: sources/virtualization/guestfs-tools/build-aux/guestfs-test-driver

## Scope

Automake-style test driver customized to record guestfs test duration.

## Behavior

- Parses standard Automake test-driver options: test name, log file, TRS file, expected failure, color, and hard-error behavior.
- Runs the supplied test script, capturing stdout/stderr to the log file.
- Maps exit status to `PASS`, `FAIL`, `SKIP`, `ERROR`, `XFAIL`, or `XPASS`.
- Writes result metadata to `.trs`, including `:guestfs-time:` measured in seconds.
- Removes log/TRS files on signal traps.

## Dependencies And Risks

- Maintained as an Automake-derived script with guestfs-specific timing metadata.
- Uses shell `set -u`, so missing mandatory option handling is strict.
- Color output uses terminal escape sequences only when enabled.
