# File Research: sources/os/bsd/netbsd-src/sys/sys/localedef.h

Defines internal locale category structures for messages, monetary formatting, numeric formatting, and time formatting. Structures mostly hold string pointers plus POSIX locale formatting fields.

There is no runtime logic. The header supports libc/localedef consumers that need structured locale data. Risks are layout compatibility and pointer lifetime of locale backing strings.
