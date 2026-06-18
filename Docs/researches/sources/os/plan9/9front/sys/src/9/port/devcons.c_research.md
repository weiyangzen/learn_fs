# File Research: sources/os/plan9/9front/sys/src/9/port/devcons.c

Purpose: core console and system-control device `#c`, plus kernel printing, panic, time, random, process identity, driver masking, and shutdown helpers.

Exposed interface: `bintime`, `cons`, `consctl`, `cputime`, `drivers`, `hostdomain`, `hostowner`, `kmesg`, `kprint`, `null`, `osversion`, `pid`, `ppid`, `random`, `reboot`, `sysname`, `sysstat`, `time`, `user`, `zero`, `config`, and `mordor`.

Core implementation: printing flows through `putstrn0`, which appends to `kmesg`, sends to `/dev/kprint` or screen output, and sends to UART/serial queues with newline conversion. `panic` disables kprint, prints diagnostic output, dumps stack, optionally exits/reboots, or hangs. `consread` handles directory reads and each virtual file’s data. `conswrite` handles console output, time setting, host/user/sysname updates, driver masks, reboot/panic/rdb commands, and sysstat reset.

Time support: text `time` returns seconds, nanoseconds, fast ticks, fast frequency, and monotonic value. `bintime` reads/writes big-endian binary time controls for setting time, adjustment, and frequency.

Dependencies: kernel queues, random, TOD/fastticks, auth/hostowner helpers, UART output, reboot/debug hooks, and global machine accounting.

Research notes: this is central kernel plumbing. Important audit areas are privilege checks around reboot/time, nonblocking kprint queue behavior, direct panic paths, and avoiding page faults or blocking in low-level print paths.
