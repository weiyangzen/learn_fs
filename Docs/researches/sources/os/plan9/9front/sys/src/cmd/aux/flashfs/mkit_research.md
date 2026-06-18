# File Research: sources/os/plan9/9front/sys/src/cmd/aux/flashfs/mkit

Role: Tiny rc script to make a local flashfs test image.

Behavior:
- Writes geometry-like values to `fs.filectl`.
- Runs `8.mkflashfs -n 16 -z 16384 -f fs.file`.

Use:
- Convenience script for creating a 16-sector, 16 KiB-sector flashfs image.
