# sources/user-network-fs/rclone/fs/bwtimetable_test.go

Purpose: provides broad tests for bandwidth pair and timetable parsing, rendering, current-limit lookup, and JSON conversion.

Important APIs/functions: interface assertions ensure `BwTimetable` satisfies `Flagger` and `FlaggerNP`. `TestBwTimetableSet` is a large table for bad inputs, constant limits, `tx:rx` limits, all-days time expansion, weekday-specific schedules, semicolon separators, and documented examples. `TestBwTimetableLimitAt` validates empty timetable unlimited behavior, exact and in-between slot selection, same-day slots, and week wraparound. JSON tests check string conversion in both directions.

Control flow: tests instantiate a fresh timetable for each parse case, call `Set`, assert error/no-error, compare the exact slot slice, and compare `String`. `LimitAt` uses fixed UTC dates with known weekdays to validate lookup.

State and persistence behavior: expected outputs document canonical string formatting such as `Sun-10:20,666Ki`, `off`, and omitted `:rx` when upload/download limits match. Empty timetable lookup returns an unlimited slot (`-1` sizes) even though empty parse input is invalid.

Dependencies and integration points: uses `encoding/json`, `time`, and `testify`. It constrains global `bwlimit` behavior consumed by transfer throttling.

Risks: the tests rely on exact expanded ordering and therefore protect compatibility but make parser output changes noisy. They do not test reusing a non-empty timetable receiver or non-UTC local timezone edge cases.

Test signals: very strong parser and lookup coverage across normal, edge, and documented cases.
