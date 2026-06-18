# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcswcs.c

Compatibility wrapper for `wcswcs()`. It defines `WCSWCS` and includes `wcsstr.c`, reusing the same wide substring implementation under the legacy symbol name.

No independent logic is present.
