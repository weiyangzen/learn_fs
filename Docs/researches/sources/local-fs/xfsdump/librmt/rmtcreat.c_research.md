# File Research: sources/local-fs/xfsdump/librmt/rmtcreat.c

Implements `rmtcreat(path, mode)`.

Behavior:
- For remote device paths, calls `rmtopen(path, 1 | O_CREAT, mode)`.
- For local paths, calls `creat(2)`.

Role:
- Compatibility wrapper mirroring `creat(2)` while supporting remote tape paths.
