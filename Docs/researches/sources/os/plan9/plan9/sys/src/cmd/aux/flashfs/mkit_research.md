# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/mkit

This is a tiny rc script for creating a sample flashfs file image.

Key behavior:
- Writes fake flash geometry to `fs.filectl`.
- Runs `8.mkflashfs -n 16 -z 16384 -f fs.file`.

Filesystem relevance:
- Direct helper script for preparing a flashfs test image.
