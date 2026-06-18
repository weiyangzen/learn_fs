# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/dump.c

Small diagnostic print helpers for core Venti structures.

Key behavior:
- `printindex` prints index name/version/blocksize/table size, bucket divider, section bucket ranges, and arena address ranges.
- `printarenapart` prints arena partition metadata and arena map entries.
- `printarena` prints arena range, version, timestamps, sealed status, optional score, clump counts, data sizes, compressed data, and storage usage.

Interactions:
- Used by check tools and verbose diagnostics.

Notable details:
- `printarena` takes an `fd` argument but several lines print to file descriptor 2 directly.
