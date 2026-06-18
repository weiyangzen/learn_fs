# File Research: sources/os/bsd/netbsd-src/lib/libc/string/__strsignal.c

Implements internal `__strsignal(num, buf, buflen)`. For known signal numbers it returns or copies `sys_siglist[num]`; for realtime signals it formats `"Real time signal %u"`; otherwise it formats `"Unknown signal: %u"`.

When NLS is enabled, it uses the libc message catalog and writes into the caller buffer; without NLS, known signals return the static `sys_siglist` string directly.
