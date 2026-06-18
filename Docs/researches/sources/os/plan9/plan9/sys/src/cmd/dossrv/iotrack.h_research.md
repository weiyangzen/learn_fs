# File Research: sources/os/plan9/plan9/sys/src/cmd/dossrv/iotrack.h

Cache/device I/O type header for `dossrv`.

Key contents:
- Defines `MLock`, `Iosect`, `Iotrack`, and `Track`.
- Establishes `Sectorsize = 512`, `Sect2trk = 9`, and `Trksize`.
- Defines buffer flags `BMOD`, `BIMM`, and `BSTALE`.
- Declares sector acquisition/release, track read/write/purge, cache init/sync, simple lock operations, and device I/O functions.

Filesystem relevance:
- Shared declarations for the FAT server’s sector-cache and backing-device layer.
