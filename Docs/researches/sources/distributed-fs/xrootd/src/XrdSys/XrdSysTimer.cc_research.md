# sources/distributed-fs/xrootd/src/XrdSys/XrdSysTimer.cc

Purpose: implements elapsed-time measurement, sleep helpers, midnight calculations, duration formatting, timezone offset calculation, and midnight waiting.

Important APIs/types/functions: implements `Delta_Time()`, static `Midnight()`, several `Report()` overloads, `Snooze()`, `s2hms()`, `TimeZone()`, `Wait()`, and `Wait4Midnight()`.

Control flow: `Reset()` in the header captures `StopWatch`; `Report()` captures now, computes delta into `LastReport`, and overloads add that delta into caller totals as seconds, milliseconds, or `timeval`. `Snooze()` and `Wait()` loop around `nanosleep()` after `EINTR`. `Midnight()` returns local midnight for a timestamp or the next 23:59:59 plus one second special case. `Wait4Midnight()` uses absolute `clock_nanosleep()` except on Apple, where it uses relative sleeps and an NTP-adjustment loop.

State and persistence: each `XrdSysTimer` instance stores `StopWatch` and `LastReport`. Static helpers do not persist state.

Dependencies and integration: uses `gettimeofday`, `time`, `localtime_r`, `mktime`, `gmtime_r`, `nanosleep`, and Windows `Sleep()` compatibility. It is used by scheduling, periodic recompute loops, and coarse elapsed-time accounting, including XrdThrottle.

Risks: wall-clock APIs are sensitive to clock adjustments; elapsed timers would be more stable with monotonic clocks. `TimeZone()` approximates offset by comparing local and GMT hours and can be wrong across DST/date boundaries. `s2hms()` calls `snprintf(buff, blen-1, ...)`, which underuses the provided size and is unsafe for `blen <= 0`.

Test signals: validate duration accumulation, EINTR sleep retry, midnight around DST transitions, formatting buffer boundaries, and `Wait4Midnight()` behavior under clock jumps.
