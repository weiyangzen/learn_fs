# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printstate.c

Live state-table entry pretty-printer.

Key behavior:
- Prints version/protocol, source/destination endpoints, TCP state, remaining lifetime, clone/orphan flags, and protocol-specific details.
- Prints packet/byte counters for forward/reverse and in/out directions.
- Reconstructs pass/block/log/count/auth action flags.
- Prints interface names/pointers, verbose packet-match metadata, and synchronization status read through `kmemcpy()`.

Research notes:
- Uses `hostname()` and optional protocol-name resolution.
