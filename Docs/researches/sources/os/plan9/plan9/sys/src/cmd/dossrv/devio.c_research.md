# File Research: sources/os/plan9/plan9/sys/src/cmd/dossrv/devio.c

Device I/O shim for the FAT server.

Key behavior:
- `devread()` reads sectors with `pread()` at `xf->offset + sector*Sectorsize`.
- `devwrite()` writes sectors with `pwrite()` unless the backing file was opened read-only.
- `devcheck()` verifies media/backing-file liveness by reading sector zero.
- `deverror()` maps short/failed I/O to `Eio`, logs details, and closes/invalidates the backing fd on hard errors.

Filesystem relevance:
- All cached FAT sector reads/writes pass through this offset-aware backing-device layer.
