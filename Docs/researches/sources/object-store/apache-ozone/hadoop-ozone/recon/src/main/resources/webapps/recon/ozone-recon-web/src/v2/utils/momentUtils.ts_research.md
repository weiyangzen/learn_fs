# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/utils/momentUtils.ts

Purpose: Centralizes compact time formatting helpers for the v2 UI and customizes Moment's English relative-time strings.

Important APIs/types/functions: Calls `moment.updateLocale('en', { relativeTime: ... })` at module load. Exports `getTimeDiffFromTimestamp(timestamp)`, `getDurationFromTimestamp(timestamp)`, and `getFormattedTime(time, format)`.

Control flow: Importing the module globally changes Moment's `en` locale relative-time output. `getTimeDiffFromTimestamp` converts a numeric timestamp to `Date` and returns `fromNow()`. `getDurationFromTimestamp` treats input as milliseconds, decomposes years/months/days/hours/minutes/seconds, returns an empty string for invalid/zero ISO `P0D`, and otherwise returns compact parts or "Just now". `getFormattedTime` formats strings directly and formats positive numeric times, returning `N/A` for nonpositive numeric values.

State and persistence: The locale mutation is global process/browser state for Moment. Helpers themselves are stateless.

Dependencies and integration points: Used wherever v2 table/cards need compact elapsed time, durations, or formatted timestamps. Depends entirely on Moment.

Risks: `moment.updateLocale` affects all Moment relative-time formatting in the app after import. `getDurationFromTimestamp(0)` returns empty string, while sub-second positive durations return "Just now"; callers need to distinguish those semantics. String times are formatted even if invalid, which can produce Moment's invalid-date output.

Test signals: Unit tests should cover past timestamps, zero/invalid duration, multi-unit durations, sub-second durations, numeric `0`, negative numbers, string dates, invalid strings, and global relative-time formatting expectations.
