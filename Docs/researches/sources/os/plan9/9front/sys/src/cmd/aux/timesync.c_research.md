# File Research: sources/os/plan9/9front/sys/src/cmd/aux/timesync.c

`timesync` is a clock synchronization daemon. It can synchronize from filesystem time, RTC, UTC file, GPS file, or NTP, adjust kernel time and frequency, optionally update RTC, and optionally serve SNTP/NTP replies on one or more networks.

It supports modern `/dev/bintime` or older `/dev/nsec` plus `/dev/fastclock`/`/dev/timing` interfaces. Time corrections can set absolute time, slew a delta over a period, and adjust frequency. `-i` makes it read-only/impotent for testing.

The main loop samples the chosen source, discards bad samples, sets time immediately if error exceeds 10 seconds, otherwise slews a damped correction, adapts the sampling period based on accuracy, estimates oscillator frequency from retained samples, caps error from frequency changes, and persists frequency under `dir` as `ts.<sysname>.<type>[.<server>]`.

NTP client mode queries configured servers, computes offset and RTT from NTP timestamps, selects the lowest metric based on root dispersion and delay, and derives local stratum/root delay/dispersion. NTP server mode listens on UDP ntp in header mode, replies to client mode 3 packets, and fills stratum, precision, root delay/dispersion, root id, reference, receive, originate, and transmit timestamps.

Options include accuracy `-a`, state directory `-d`, debug `-D`, filesystem `-f`, GPS `-G`, root id `-I`, logging `-l`, local-time RTC correction `-L`, NTP `-n`, RTC `-r`, serve network `-s`, stratum `-S`, and UTC `-U`.

Caveats: code assumes Plan 9 clock devices and kernel write protocols; root ID defaults vary by source; several source failures shorten retry period but otherwise continue.
