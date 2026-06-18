# sources/storage-engines/rocksdb/options/offpeak_time_info.h

Purpose: declares the small off-peak scheduling model used by RocksDB options code to represent daily UTC maintenance windows.

Important APIs, types, and functions: `OffpeakTimeInfo` is a result struct containing `is_now_offpeak` and `seconds_till_next_offpeak_start`. `OffpeakTimeOption` stores constants for day/hour/minute lengths, constructors, the original `daily_offpeak_time_utc` string, parsed `daily_offpeak_start_time_utc` and `daily_offpeak_end_time_utc`, plus `SetFromOffpeakTimeString` and `GetOffpeakTimeInfo`.

Control flow: users construct or update the option from a string, then ask for off-peak status at a supplied timestamp. The implementation is intentionally clock-independent at the public method boundary, which makes scheduling callers responsible for obtaining UTC time.

State and persistence behavior: the persisted representation is the string form; parsed integer fields are derived runtime state. Defaults leave all fields empty/zero, which the implementation treats as no off-peak window.

Dependencies and integration points: references `rocksdb/rocksdb_namespace.h` and forward-declares `SystemClock`. It is conceptually tied to `MutableDBOptions::daily_offpeak_time_utc` and compaction trigger scheduling but has no heavy RocksDB dependencies in the header.

Risks: callers may confuse UTC strings with local time. Start/end seconds are public fields, so external mutation can bypass parse validation. The all-zero default is both a valid internal sentinel and a possible parsed equal-start/end state, so consumers should rely on `GetOffpeakTimeInfo`.

Test signals: this header has no direct test in the subset. It is indirectly represented by DB options parsing tests for the string field; algorithmic tests should cover same-day ranges, overnight ranges, equal endpoints, invalid strings, and exact boundary minutes.
