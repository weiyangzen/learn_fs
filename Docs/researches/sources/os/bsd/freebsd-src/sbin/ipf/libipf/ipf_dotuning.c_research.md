# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ipf_dotuning.c

Command helper for listing, reading, and setting IPFilter tunables through ioctl objects.

Key behavior:
- Builds an `ipfobj_t` wrapping `ipftune_t` with type `IPFOBJ_TUNEABLE`.
- Parses comma-separated tuning arguments.
- `list` iterates with `SIOCIPFGETNEXT`; `name=value` uses `SIOCIPFSET`; bare `name` uses `SIOCIPFGET`.
- Prints results with `printtunable()` and reports ioctl errors through `ipf_perror_fd()`.

Research notes:
- `strtok()` mutates the caller-provided tuning string.
- Values are parsed as unsigned long only.
