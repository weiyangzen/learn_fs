# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printaps.c

Application proxy session printer.

Key behavior:
- Reads proxy session and proxy descriptor from kernel memory.
- Prints proxy label, protocol, refcount, flags, bytes/packets, and data presence.
- In verbose TCP mode, prints state/selection and sequence/ack adjustment data.
- Knows specific layouts for RealAudio, FTP, and IPSec proxy private data.

Research notes:
- Depends on `kmemcpy()` and kernel structure layout compatibility.
