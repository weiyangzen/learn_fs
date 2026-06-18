# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/strtty.h

`strtty.h` defines legacy STREAMS TTY subsystem structures and constants. `t_buf` describes an input or output message/data buffer with message pointer, current buffer pointer, and count. `strtty` aggregates input/output buffers, read queue, ioctl block, large buffer, device number, termios-style flag fields, internal state, line discipline, device status, and control-character array.

The header defines a 512-byte large buffer size, input/output priorities (`TTIPRI`, `TTOPRI`), many internal TTY state bits (`TIMEOUT`, `WOPEN`, `ISOPEN`, `CARR_ON`, `BUSY`, `WIOC`, `TTSTOP`, `EXTPROC`, `RTO`, `TTXON`, `TTXOFF`, etc.), and device command numbers for output, timeout, suspend/resume, flow block/unblock, flushes, break, input, disconnect, parameter changes, and switch.

It also defines STREAMS `M_CTL` control message subtypes for canonicalization negotiation and device-specific service behavior, including POSIX close semantics probes. The constants are legacy-heavy and partly overlapping (`MC_PART_CANON` and `MC_SERVICEIMM` both use value 3), reflecting historical STREAMS TTY module/driver conventions.
