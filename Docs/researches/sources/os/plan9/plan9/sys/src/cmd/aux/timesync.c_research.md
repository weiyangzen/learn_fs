# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/timesync.c

Time synchronization daemon/client with optional NTP serving. It can synchronize local time from filesystem time, RTC, UTC file, GPS file, or NTP servers, and it can serve SNTP/NTP responses on specified networks.

Time sources:
- `Fs`: filesystem server time, default via `/srv/boot`.
- `Rtc`: `/dev/rtc`.
- `Utc`: external UTC file.
- `Gps`: GPS time file, default `/mnt/gps/time`.
- `Ntp`: one or more NTP servers, default `$ntp`.

Core loop:
- Initializes kernel clock interface and current frequency.
- Reads persisted frequency from a per-system file in `dir` default `/tmp`.
- Samples the selected source.
- If local time differs by more than 10 seconds, steps the clock.
- Otherwise slews a fraction of the delta and adjusts next sampling interval.
- Maintains samples up to one day to estimate clock frequency.
- Persists frequency periodically.

Kernel clock interfaces:
- `/dev/bintime` preferred.
- `/dev/nsec`, `/dev/fastclock`, and optionally `/dev/timing` fallback.
- Supports setting absolute time, frequency, and slewing delta.

NTP behavior:
- `ntptimediff()` sends SNTP client requests and computes offset and RTT.
- `ntpsample()` chooses the server with the best root dispersion/delay metric.
- `ntpserver()` answers client mode 3 requests with local stratum, root delay/dispersion, root ID, and timestamps.

Important functions:
- `adjustperiod()`, `caperror()`, `whatisthefrequencykenneth()` implement control-loop timing/frequency logic.
- `hnputts()`, `nhgetts()`, `hnputfp()`, `nhgetfp()` convert NTP timestamp/fixed-point fields.
- `sample()` samples second-resolution sources at a transition edge.
- `background()` daemonizes after the first loop unless debug mode is set.

Dependencies and integration:
- Uses Plan 9 IP, auth, arbitrary precision `mp`, clock devices, network dialing/announce, syslog, and process priority controls.
- Uses `/proc/<pid>/ctl` to set priority and wire to processor 2.

Notable risks:
- Time-setting code is high-impact and system-specific.
- NTP support is minimal SNTP-style and does not authenticate packets.
- Duplicate prototypes for `hnputts()` and `nhgetts()` appear in declarations.
- Some arithmetic mixes signed and unsigned wide values; behavior depends on Plan 9 compiler/runtime assumptions.
