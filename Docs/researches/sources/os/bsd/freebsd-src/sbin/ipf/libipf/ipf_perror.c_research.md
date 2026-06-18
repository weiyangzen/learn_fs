# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ipf_perror.c

IPFilter-aware error reporting wrapper.

Key behavior:
- `ipf_perror()` prints a message with an internal IPFilter error string when available.
- `ipf_perror_fd()` preserves `errno`, asks the device for `SIOCIPFINTERROR`, prints the internal code prefix, and returns the internal error or saved `errno`.
- `ipferror()` chooses IPFilter error retrieval for valid file descriptors and normal `perror()` otherwise.

Research notes:
- Output goes directly to `stderr`.
