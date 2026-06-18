# sources/user-network-fs/rclone/fs/bwtimetable.go

Purpose: implements bandwidth limit parsing and lookup for rclone global and per-file bandwidth timetables.

Important APIs/types/functions: `BwPair` stores upload `Tx` and download `Rx` as `SizeSuffix`; methods are `String`, `Set`, and `IsSet`. `BwTimeSlot` stores weekday, HHMM time, and a `BwPair`. `BwTimetable` is a slice of slots with `String`, `Set`, `LimitAt`, `Type`, `UnmarshalJSON`, and `MarshalJSON`. Helpers include `validateHour`, `parseWeekday`, and `timeDiff`.

Control flow: `BwPair.Set` accepts either one size for both directions or `tx:rx`. `BwTimetable.Set` rejects empty input; a single value with no space/comma becomes a constant Sunday-midnight slot. Otherwise it splits tokens by spaces or semicolons. Tokens without a weekday expand a time to all seven weekdays; tokens with `Day-HH:MM` create one slot. Each token parses bandwidth through `BwPair.Set`. `LimitAt` computes current weekday/time as `DHHMM`, defaults to the last slot for wraparound, then chooses the closest slot not after the requested time.

State and persistence behavior: the timetable is stored as an ordered slice. The code does not sort slots after parsing; lookup correctness relies on scanning all slots for closest prior time and uses the last slot as wraparound. JSON persists the same string representation used by flags.

Dependencies and integration points: uses `SizeSuffix`, rclone flag interfaces, JSON config, and `time.Time`. It is wired into global options `bwlimit` and `bwlimit_file` in `fs/config.go`.

Risks: because `Set` appends to the receiver, callers reusing a non-empty `BwTimetable` without clearing it can accumulate slots. Time parsing checks length and numeric ranges but does not explicitly require the separator at index 2 to be `:`, relying on failed minute parsing for malformed strings. Slot ordering is display order from input expansion, not normalized chronological order.

Test signals: `bwtimetable_test.go` extensively covers invalid formats, constant and directional limits, daily expansion, weekday-specific entries, semicolon separators, wraparound lookup, and JSON marshal/unmarshal.
