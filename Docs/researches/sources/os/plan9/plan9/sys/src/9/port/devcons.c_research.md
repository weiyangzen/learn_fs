# File Research: sources/os/plan9/plan9/sys/src/9/port/devcons.c

Implements `#c`, the central console and miscellaneous kernel pseudo-device. The namespace includes console I/O (`cons`, `consctl`, `kprint`, `kmesg`), time (`time`, `bintime`), identity/configuration (`hostowner`, `hostdomain`, `sysname`, `user`, `config`, `osversion`), process ids, CPU/system stats, memory/swap stats, `random`, `null`, `zero`, `drivers`, and privileged reboot control.

Console output routes through `putstrn0`: it records messages in the `kmesg` ring buffer, sends to `/dev/kprint` if open, otherwise to screen output when available, and also to serial/UART output. `print`, `iprint`, `panic`, `sysfatal`, and `_assert` build on this path.

Keyboard input is staged at interrupt time into `kbd.istage`, drained by a periodic clock callback, echoed, and then processed into raw or line mode. `consctl` supports `rawon`, `rawoff`, `ctlpon`, and `ctlpoff`. The `^T ^T` escape path triggers debugging actions such as stack dump, process dump, scheduler dump, memory summaries, reboot, and toggling `consdebug`.

`consread` provides formatted views of CPU time, process IDs, system stats, swap/memory status, driver table, kernel config, and time. Reads of `cons` block until line-mode input is available unless raw mode changes flushing behavior. `kprint` is exclusive and uses a queue for kernel output capture.

`conswrite` handles console output, time setting by `eve`, host/user writes via external helpers, reboot/halt/panic commands, sysstat counter reset, swap channel setup, pager start, and sysname update. Time support includes text and binary little-endian formats with fast tick frequency management.

Dependencies span keyboard queues, UART/screen hooks, random/tod APIs, pager/swap, reboot, process structures, and pool stats. This file is a high-centrality kernel device with broad side effects.
