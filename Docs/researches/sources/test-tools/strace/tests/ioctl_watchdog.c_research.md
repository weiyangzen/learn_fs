<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_watchdog.c -->
# sources/test-tools/strace/tests/ioctl_watchdog.c

Purpose: Tests decoding of Linux watchdog `WDIOC*` ioctl commands, including support-query structures, integer getter/setter commands, option flags, keepalive, and unknown watchdog ioctl numbers.

Important APIs/types/functions: Uses `ioctl`, `<linux/watchdog.h>`, `struct watchdog_info`, xlat table `watchdog_ioctl_cmds`, `do_ioctl`, `do_ioctl_ptr`, optional `INJECT_RETVAL` lock-on logic, and compile-time `VERBOSE` for detailed identity printing.

Control flow: With injection enabled, the program loops on `WDIOC_GETSUPPORT` until the injected return is observed. It then allocates and fills `watchdog_info`, tries support decoding, iterates simple integer getters, tests timeout setters, decodes `WDIOC_SETOPTIONS` for known and unknown `WDIOS_*` bits, emits `WDIOC_KEEPALIVE`, and tests an unknown `_IOC(_IOC_NONE, 'W', 0xff, 0)` command.

State/persistence behavior: Normal operation uses fd `-1`, so it creates no watchdog state. In-memory buffers and `errstr` carry state between syscall and printf. The success wrappers use injection only.

Dependencies: Linux watchdog UAPI headers, strace xlat macros, and fault-injection support for success variants.

Integration points: Validates ioctl command-name xlat lookup, watchdog option/identity structure decoding, integer pointer rendering, verbose truncation behavior, and injected-success `=>` handling.

Risks: Watchdog option flags can grow; verbose and abbreviated variants must agree on which fields are elided. Injection argument handling is a separate failure mode.

Test signals: Expected output includes support structure or pointer fallback, simple getter/setter lines, `WDIOS_*` flags, keepalive with no argument, unknown ioctl formatting, injected markers in success builds, and final exit.

Source read signal: complete file read for this research pass; file size 169 line(s), 4288 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_watchdog.c -->
