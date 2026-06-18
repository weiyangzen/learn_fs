# sources/sync-backup/syncthing/lib/stringutil/stringutil.go

Purpose: small string/time formatting utilities.

Important APIs and control flow: `UniqueTrimmedStrings` trims ASCII space characters from both ends of each string, preserves first-seen order, and removes duplicates using a map. It returns nil for nil input because the result slice starts nil and no append occurs. `NiceDurationString` rounds durations to coarser units as magnitude grows: hours above a day, minutes above an hour, seconds above a minute, milliseconds above a second, and microseconds above a millisecond.

State and persistence: pure functions, no state.

Dependencies and integration: uses `strings` and `time`; likely feeds configuration/display normalization.

Risks: trimming uses `strings.Trim(v, " ")`, not Unicode whitespace. `NiceDurationString` uses strict greater-than thresholds, so exact boundary values are not rounded at the next unit. Tests cover uniqueness/trimming only.
