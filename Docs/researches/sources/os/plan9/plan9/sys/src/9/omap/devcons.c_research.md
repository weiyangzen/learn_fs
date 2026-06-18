# File Research: sources/os/plan9/plan9/sys/src/9/omap/devcons.c

Implements the OMAP console device `#c`, kernel printing, console input processing, kmesg/kprint, time files, random, reboot, and system status interfaces.

Key points:
- Defines global console queues: raw keyboard input, processed line input, serial output, and `/dev/kprint` output.
- `printinit()` creates the processed input queue; `consactive()`/`prflush()` observe pending serial output.
- Keeps a rolling `kmesg` buffer for boot/runtime messages.
- `putstrn0()` routes output to `/dev/kprint`, screen, UART, and serial queue, converting newline to CRLF for serial unless raw.
- `print()`, `iprint()`, `panic()`, `sysfatal()`, `_assert()`, and `pprint()` provide kernel/user-visible printing and panic behavior.
- Input path stages interrupt-time characters in `kbd.istage`, flushes them on a clock callback, handles raw/cooked mode, echo, ^U/^D/newline, and ^T debug commands.
- Exposes many files under `#c`: `bintime`, `cons`, `consctl`, `cputime`, `drivers`, `hostdomain`, `hostowner`, `kmesg`, `kprint`, `null`, `osversion`, `pgrpid`, `pid`, `ppid`, `random`, `reboot`, `swap`, `sysname`, `sysstat`, `time`, `user`, and `zero`.
- `consread()` implements each file, including process IDs, CPU time, sysstat, swap stats, driver list, zero/random, and time.
- `conswrite()` handles console output, raw/ctlp toggles, time setting, owner/domain/user writes, reboot commands, sysstat reset, swap setup, and sysname setting.
- Implements endian helpers and binary/text time read/write, including `todset()`, `todsetfreq()`, and `fastticks()` frequency setup.
- `nrand()`/`rand()` provide a simple random fallback seeded from `randomread()`.

Dependencies and interactions:
- Uses UART queues from `devuart.c`, screen output hook, TOD/random subsystems, reboot paths, pager/swap, and process tables.
- Clock callback installed in `consinit()` drains staged keyboard input.
- `panic()` ultimately calls `exit()`.

Research relevance:
- Full console and system-control filesystem for the OMAP kernel, central to boot diagnostics and runtime administration.
