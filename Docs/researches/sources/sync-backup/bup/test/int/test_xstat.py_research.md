# sources/sync-backup/bup/test/int/test_xstat.py

Purpose: tests filesystem timestamp conversion helpers in `bup.xstat`, especially negative timestamp rounding and integer type preservation.

Important APIs/types/functions: `xstat.timespec_to_nsecs`, `nsecs_to_timespec`, `nsecs_to_timeval`, and `fstime_floor_secs`.

Control flow: a single test asserts conversions between `(sec,nsec)` pairs and nanoseconds, nanoseconds to timespec, nanoseconds to timeval microseconds, and floor-to-seconds behavior for positive and negative half-second values.

State and persistence behavior: pure arithmetic tests with no filesystem mutation despite targeting filesystem timestamp formats.

Dependencies/integration points: timestamp conversion is used by metadata/index code to preserve stat times across platforms and before/after the Unix epoch.

Risks and test signals: negative timestamp handling is easy to get wrong due to floor versus truncation semantics. Signals are exact numeric equality and checks that returned tuple elements remain Python ints.
