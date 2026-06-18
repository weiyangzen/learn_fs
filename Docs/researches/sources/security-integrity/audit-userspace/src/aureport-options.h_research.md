# sources/security-integrity/audit-userspace/src/aureport-options.h

## Purpose
`aureport-options.h` defines the report mode contract for `aureport`. It exposes report type/detail enums, global option state, and the command-line parser entry point.

## Important APIs, Types, And Functions
It defines `report_type_t` with summary, AVC, MAC, config, event, file, host, login, account modification, PID, syscall, terminal, user, executable, anomaly, response, crypto, auth, key, TTY, command, virtualization, and integrity reports. It defines `report_det_t` for summary/detailed/specific output and declares `report_type`, `report_detail`, `report_format`, and `check_params`. It also defines the `UNIMPLEMENTED` exit macro.

## Control Flow
No runtime flow exists in the header. It lets `aureport-options.c` set modes and lets scan/output modules branch on those modes.

## State And Persistence
The declared globals are process-wide state. They persist for the lifetime of one `aureport` run and shape scan and output behavior.

## Dependencies And Integration
It includes `ausearch-common.h`, tying report formatting to common ausearch/aureport types such as `report_t`. It is used by option parsing and output code.

## Risks
The `UNIMPLEMENTED` macro prints and exits from wherever invoked, making partial option paths abrupt and hard to unit test. New report types require synchronized changes in option parsing, scanning, titles, detailed output, and summaries.

## Test Signals
Compile coverage is necessary whenever adding enum values. Behavioral tests should verify every enum has parser and output handling and that `UNIMPLEMENTED` paths are intentional.
