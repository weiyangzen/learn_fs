# File Research: sources/os/bsd/dragonflybsd/sys/sys/kerneldump.h

Defines kernel dump header format and dump I/O interface. `kerneldumpheader` stores magic, architecture, dump version, length, time, block size, hostname, version string, panic string, and parity. Endian conversion macros encode dump byte order.

Kernel APIs include `mkdumpheader`, dumper callback type `dumper_t`, `struct dumperinfo`, `set_dumper`, `dump_write`, `dumpsys`, `md_dumpsys`, and CPU reactivation. Relevant to storage because dump devices implement the low-level writer described by `dumperinfo`.
