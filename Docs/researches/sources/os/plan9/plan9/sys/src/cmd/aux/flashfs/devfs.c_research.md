# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/devfs.c

This file abstracts flashfs block storage over either a flash device or a plain file.

Key behavior:
- Opens a data file/device and optionally a matching `ctl` file.
- Reads flash geometry from the control file when using a flash device.
- Falls back to plain-file mode with explicit or stat-derived sector count/size.
- Erases sectors either by writing all-ones blocks or by issuing `erase` to the device control file.
- Provides sector-relative `readdata` and `writedata`.

Important details:
- Requires reasonable sector counts and sector sizes.
- Plain-file erase uses a cached all-ones sector buffer.
- `writedata` can either return failure for recoverable write attempts or fatal on short/error writes.

Filesystem relevance:
- Direct: storage backend layer for the flashfs journal filesystem.
