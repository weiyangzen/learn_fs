# File Research: sources/os/bsd/openbsd-src/sbin/dmesg/dmesg.c

## Purpose
Prints the kernel message buffer, either from the running kernel via `sysctl(3)` or from a kernel/core image via `kvm(3)`.

## Key Behavior
- Parses `-s`, `-M core`, and `-N system`.
- Without `-M/-N`, reads live message buffers using `KERN_MSGBUFSIZE`/`KERN_MSGBUF` or startup console buffers with `KERN_CONSBUFSIZE`/`KERN_CONSBUF`.
- With `-M/-N`, locates `_msgbufp` via `kvm_nlist()`, reads the `struct msgbuf`, validates `MSG_MAGIC`, and reads backing message bytes.
- Drops to `pledge("stdio")` after acquiring buffer access.
- Walks the circular buffer starting at `msg_bufx`.
- Skips syslog priority sequences that appear as newline followed by `<...>`.
- Uses `vis()` before printing characters so non-printable data is safely escaped.

## Notes
The implementation is careful about both live and offline message sources and avoids emitting raw control bytes.
