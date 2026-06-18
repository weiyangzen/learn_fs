# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/epoch.c

Standalone tool for reading or editing the low epoch in a fossil superblock.

It opens the disk read-only or read-write depending on whether a new low epoch was supplied, unpacks the header, reads the superblock, prints `epoch <low>`, and optionally writes a modified `epochLow` back.

It bypasses the full cache/filesystem layer and directly uses `headerUnpack`, `superUnpack`, and `superPack`.
