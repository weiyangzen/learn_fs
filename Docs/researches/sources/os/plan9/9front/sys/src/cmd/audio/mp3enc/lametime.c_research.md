# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/lametime.c

## Scope
Time and file utility implementation for the LAME frontend.

## APIs and Behavior
`GetCPUTime()` returns process CPU time via `clock() / CLOCKS_PER_SEC`. `GetRealTime()` returns wall time from `gettimeofday()` and asserts on failure. `lame_set_stream_binary_mode()` is a no-op returning 0, matching Unix/Plan 9 stream semantics. `lame_get_file_size()` returns `stat().st_size` or `-1`.

## Dependencies
Uses standard/POSIX headers: `time.h`, `sys/time.h`, `sys/types.h`, `sys/stat.h`, plus `lametime.h`.

## Risks and Notes
`GetRealTime()` uses `assert(0)` for an OS error path. Binary mode is intentionally ignored here, unlike DOS/Windows ports.
