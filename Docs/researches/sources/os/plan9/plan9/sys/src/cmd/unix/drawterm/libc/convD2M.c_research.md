# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/convD2M.c

This file serializes `Dir` structures into 9P stat message format.

Key behavior:
- `sizeD2M` computes packed stat size.
- `convD2M` writes fixed fields, qid, mode/times/length, and counted strings for name, uid, gid, and muid.

Important details:
- Writes the size field before returning `BIT16SZ` for too-small buffers, allowing callers to discover needed size.
- Uses little-endian 9P `PBIT*` macros.
