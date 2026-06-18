# sources/storage-engines/rocksdb/options/offpeak_time_info.cc

Purpose: implements parsing and evaluation for the daily off-peak UTC time range used by mutable DB options such as `daily_offpeak_time_utc`.

Important APIs, types, and functions: `OffpeakTimeOption::OffpeakTimeOption()` delegates to the string constructor with an empty range. `SetFromOffpeakTimeString` calls `TryParseTimeRangeString` to populate `daily_offpeak_start_time_utc` and `daily_offpeak_end_time_utc`, and only updates `daily_offpeak_time_utc` when parsing succeeds. `GetOffpeakTimeInfo` evaluates a Unix-time-like `current_time` and returns `OffpeakTimeInfo` with `is_now_offpeak` and `seconds_till_next_offpeak_start`.

Control flow: parsing saves the old start/end values, attempts to parse the new string, commits the display string on success, and restores start/end on failure. Evaluation returns default false/zero if start equals end, floors current time to the nearest minute for in-window checks, handles both same-day and overnight ranges, and computes the next start by either subtracting from today's start or wrapping by one day.

State and persistence behavior: state is in-memory and consists of the original accepted string plus parsed start/end seconds from midnight UTC. Invalid updates do not overwrite the accepted string or parsed times, so a bad runtime option update leaves the previous schedule intact. The option string itself is persisted as a regular mutable DB option by the surrounding options machinery.

Dependencies and integration points: uses `TryParseTimeRangeString` from `util/string_util.h`; includes `rocksdb/system_clock.h` but this implementation takes the current timestamp as an argument instead of reading a clock directly. It integrates with `MutableDBOptions::daily_offpeak_time_utc` and compaction scheduling logic that can use the returned `OffpeakTimeInfo`.

Risks: `current_time % 86400` assumes non-negative epoch seconds; negative timestamps would produce negative seconds since midnight in C++. The range comparison is inclusive at both start and end after minute truncation. Empty or invalid ranges collapse to start == end, which disables off-peak behavior. The function computes seconds to next start even when already off-peak, returning the next day's start rather than zero.

Test signals: no local test in this subset directly targets `OffpeakTimeOption`; indirect coverage comes from `DBOptionsAllFieldsSettable`, which parses `daily_offpeak_time_utc=08:30-19:00` as a mutable DB string field. Dedicated boundary tests for overnight windows, invalid updates, and minute rounding would reduce risk.
