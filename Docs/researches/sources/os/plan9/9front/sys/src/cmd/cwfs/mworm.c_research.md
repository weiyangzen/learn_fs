# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/mworm.c

Purpose: Implements composite block devices used by cwfs: concatenation, interleaving, partitions, and mirrors.

Key behavior:
- `mcatinit()` initializes all child devices, records `ndev`, stores a child pointer array in `private`, and caches child sizes.
- `mcatsize()`, `mcatread()`, and `mcatwrite()` concatenate child devices by cumulative block ranges.
- `mlevinit()`, `mlevsize()`, `mlevread()`, and `mlevwrite()` implement striped/interleaved devices: logical block `b` maps to child `b % ndev`, child block `b / ndev`.
- `partinit()`, `partsize()`, `partread()`, and `partwrite()` expose percentage-based partitions of an underlying device.
- `mirrinit()`, `mirrsize()`, `mirrread()`, and `mirrwrite()` implement mirror devices. Reads try mirrors in order until one succeeds; writes recurse through links so mirrors are written before the main device.

Notable details:
- Mirror writes are synchronous and deliberately ordered so a crash does not leave the main copy ahead of mirror copies.
- Composite sizes are cached on child `Device.size` but lazily filled if zero.
