# File Research: sources/os/plan9/plan9/sys/src/9/teg2/devcons.c

Plan 9 `#c/cons` device implementation for Tegra, covering console I/O, kernel message log, panic/print paths, keyboard input staging, time files, random, reboot, swap control, and basic identity files.

Key responsibilities:
- Initializes console queues and nonblocking line queue.
- Implements kernel print paths: `print`, `iprint`, `panic`, `pprint`, `putstrn`, kmesg logging, serial/screen/kprint fanout, and panic shutdown.
- Stages interrupt-time keyboard/UART input and flushes it periodically to queues.
- Handles line editing, raw mode, echoing, and `^T` debug commands.
- Implements `#c` files including `cons`, `consctl`, `kmesg`, `kprint`, `cputime`, `drivers`, `hostowner`, `hostdomain`, `pid`, `pgrpid`, `ppid`, `random`, `reboot`, `swap`, `sysname`, `sysstat`, `time`, `bintime`, `user`, `zero`, `null`, `osversion`, and `config`.
- Implements little-endian binary time read/write conversion and time-frequency adjustment commands.
- Implements random helpers `nrand` and `rand`.

Important behavior:
- `iprint` uses a best-effort lock to avoid interleaved MP output without deadlocking when a CPU is already dying.
- `panic` disables `/dev/kprint`, prints through interrupt-safe output, optionally enters `consdebug`, flushes, delays, and exits.
- `Qreboot` accepts `halt`, `reboot`, and `panic`; `halt` calls `reboot(nil, 0, 0)`.
- `Qsysstat` write resets per-Mach counters.

Dependencies and assumptions:
- Depends on Plan 9 queue, device, tod, random, process, pager, reboot, and auth/user helpers.
- Console input is normally supplied by UART code through `kbdcr2nl` or `kbdputc`.

Notable risks:
- `kbd.istage` is a finite interrupt-time ring; overflow drops input.
- `Qkmesg` reads are intentionally unlocked and can see a slurred buffer.
- `/dev/reboot panic` deliberately faults through `*(ulong*)0=0`.
