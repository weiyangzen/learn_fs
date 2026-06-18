# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devcons.c

Implements the Plan 9 console device `#c`, including console I/O, keyboard processing, time files, random/zero/null, host identity files, reboot control, clipboard bridge, and diagnostic output.

Key behavior:
- Initializes `kbdq` and `lineq` queues for raw and cooked keyboard input.
- Implements `print`, `panic`, `pprint`, `iprint`, console flushing, and `/dev/kprint`.
- Handles cooked console editing for backspace, line kill, newline, and EOF.
- Supports raw mode and `ctlpoff`/`ctlpon` through `consctl`.
- Handles keyboard compose sequences through `latin1`.
- Exposes files such as `cons`, `consctl`, `time`, `bintime`, `random`, `zero`, `null`, `drivers`, `hostowner`, `hostdomain`, `sysname`, `snarf`, `secstore`, and `reboot`.
- Reads textual and binary time using `todget`, `fastticks`, and little-endian packing helpers.
- Allows privileged writes to `time`, `bintime`, and `reboot`.

Important interfaces:
- `readnum` and `readstr` are general helpers used across other devices.
- `kbdputc` and `kbdcr2nl` are input entry points.
- `consdevtab` registers device character `c`.

Notable risks:
- Several control files are simplified drawterm adaptations; `sysstat` and `swap` are mostly stubs.
- `secstorebuf` is a fixed 64 KiB in-memory buffer.
- `snarf` bridges to host clipboard via `clipread` and `clipwrite`.
