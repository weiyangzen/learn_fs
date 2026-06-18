# sources/user-network-fs/s3fs-fuse/src/filetimes.cpp

## Purpose
Implements portable helpers for POSIX `timespec` and `stat` timestamp handling, plus the `FileTimes` value object used by s3fs cache and FUSE operations to carry ctime, atime, and mtime updates. It normalizes `UTIME_NOW` to an actual realtime timestamp and treats `UTIME_OMIT` as "do not change this field."

## Important APIs, Types, And Functions
Utility functions include `valid_timespec()`, `compare_timespec(timespec,timespec)`, `compare_timespec(stat,type,timespec)`, `set_timespec_to_stat()`, `set_stat_to_timespec()`, `str_stat_time()`, `s3fs_realtime()`, and `s3fs_str_realtime()`. `FileTimes::Clear()` and typed clear helpers set fields to `{0, UTIME_OMIT}`. `GetTime()` and typed getters return or copy a field. `ReflectFileTimes()` writes non-omitted fields into a `struct stat`. `SetTime()` resolves `UTIME_NOW`; `SetAllNow()` uses a single realtime sample; `SetAll()` overloads populate the object from `stat`, raw timespecs, or another `FileTimes`; `IsOmit()` checks the sentinel.

## Control Flow
`set_timespec_to_stat()` and `set_stat_to_timespec()` branch on `stat_time_type` and on `__APPLE__` to use `st_atimespec`/`st_mtimespec`/`st_ctimespec` on macOS or `st_atim`/`st_mtim`/`st_ctim` elsewhere. `s3fs_realtime()` tries `clock_gettime(CLOCK_REALTIME)` and falls back to `time(nullptr)` with nanoseconds zero on failure. `FileTimes::SetAll()` samples current time once, then resolves each argument: `UTIME_NOW` becomes that shared sample, and `UTIME_OMIT` is skipped unless `no_omit` allows setting omitted values.

## State And Persistence Behavior
`FileTimes` stores three `timespec` fields in memory only. The default state and cleared state are all omitted. Calling `SetTime()` with `UTIME_NOW` persists the resolved timestamp, not the sentinel, so later reflection is deterministic. The class itself performs no locking; callers such as `FdEntity` protect it when stored in shared cache state.

## Dependencies And Integration Points
This file depends on `filetimes.h`, `s3fs_logger.h`, and `string_util.h`. It integrates with metadata conversion in `metaheader.cpp`, cache entity timestamp storage in `fdcache_entity`, and FUSE operations that need `utimens`-style semantics. `str_stat_time()` and `s3fs_str_realtime()` provide string formatting through the project `str(timespec)` helper.

## Risks
`valid_timespec()` rejects negative seconds and sentinel nanoseconds but does not validate the normal nanosecond range below one billion. Unknown `stat_time_type` values log and either skip writes or return zero, which is safe but can hide enum misuse. `SetAll(..., no_omit)` semantics are subtle: when `no_omit` is false, omitted values may be propagated into the object; when true, omitted values are skipped. Any caller expecting `UTIME_NOW` to remain symbolic will be surprised because it is eagerly resolved.

## Test Signals
Tests should compare timestamps across equal, earlier, and later nanosecond values; verify macOS/non-macOS stat field mapping under platform builds; check `UTIME_NOW` resolution and `UTIME_OMIT` skipping; verify `ReflectFileTimes()` leaves omitted stat fields unchanged; and simulate `clock_gettime` failure if the test harness supports it. Integration tests around `utimens`, file creation, cache open, and metadata round-trip should observe correct atime/mtime/ctime behavior.
