# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postio/ifdef.h

`ifdef.h` centralizes platform conditional includes and external declarations for `postio`’s platform-specific code.

Key contents:
- For `SYSV`, includes `<termio.h>` and optional STREAMS headers.
- For `V9`, includes `<sys/filio.h>` and `<sys/ttyio.h>`, and declares external `tty_ld`.
- For `BSD4_2`, includes `<sgtty.h>`, `<sys/time.h>`, `<errno.h>`, defines simple `FD_ZERO`/`FD_SET`, and declares `errno`.
- For `DKHOST`, includes Datakit headers and declares Datakit helpers.
- Declares shared globals from `postio.c`: tty line name, input/output fds, log file, message buffer state, baud/stop bits, interactive mode, process role, and read/write capability flags.

This header is glue between `postio.c` and `ifdef.c`; it has no behavior itself.
