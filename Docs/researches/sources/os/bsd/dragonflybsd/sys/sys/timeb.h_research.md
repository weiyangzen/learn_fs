# File Research: sources/os/bsd/dragonflybsd/sys/sys/timeb.h

Legacy `ftime(2)` time structure and prototype.

Key contents:
- Ensures `time_t` is declared.
- Defines deprecated `struct timeb`:
  - seconds since epoch
  - milliseconds
  - timezone minutes west of UTC
  - DST flag
- Userland-only legacy prototype:
  - `ftime(struct timeb *)`

Important behavior:
- `ftime` is exposed only under BSD visibility or old XSI visibility.
- The header is retained for source compatibility.

Research notes:
- This is a legacy ABI compatibility header.
- New code should use `clock_gettime`/`gettimeofday` style APIs instead.
