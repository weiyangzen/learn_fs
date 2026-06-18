# sources/sync-backup/borg/docs/usage/general/date-time.rst.inc

Purpose: documents Borg date/time formatting and accepted timespan suffixes.

Important APIs and control flow: Borg displays ISO 8601-style dates and 24-hour times, stores/processes UTC internally, and generally displays local time. TIMESPAN accepts numeric years, months, weeks, days, hours, minutes, or seconds using suffixes such as `2y`, `12m`, `2w`, `7d`, `8H`, `30M`, `150S`.

State and persistence: no state; defines parsing/display contracts used by filters and timestamps.

Dependencies and integration points: archive filters (`--oldest`, `--newest`, `--older`, `--newer`), archive timestamps, output formatting, and placeholder expansion.

Risks: suffix case matters for months/minutes and hours/seconds examples. Local display versus UTC storage can confuse automation around time zones.

Test signals: parsing tests for all suffixes, timezone-aware timestamp handling, and deterministic formatting in command outputs.
