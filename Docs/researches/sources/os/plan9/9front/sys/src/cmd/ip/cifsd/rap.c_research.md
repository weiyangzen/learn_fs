# File Research: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/rap.c

Implements a subset of SMB RAP transaction handling.

Key points:
- `padname` writes fixed-size NUL-padded share/server names.
- `packshareinfo` handles share info levels:
  - level 0: share name only
  - level 1: name, type, remark
  - level 2: name, type, permissions/max uses/current uses, remark, and root
- `transrap` unpacks RAP command, parameter descriptor, and data descriptor strings.
- Supports RAP calls:
  - `NetShareEnum` (`0x0000`) returning the `local` share.
  - `NetShareGetInfo` (`0x0001`) for a named share.
  - `NetServerGetInfo` (`0x000d`) levels 0 and 1.
  - `NetWrkstaGetInfo` (`0x003f`) level 10.
- Packs RAP status/count/length metadata into transaction parameter output and data into transaction data output.
- Logs unknown RAP commands or levels and returns DOS/RAP status codes where appropriate.

Dependencies and interactions:
- Uses `mapshare`, `pack`/`unpack`, SMB 8-bit string packers, `sysname`, `domain`, and `osname`.
- Called by transaction command handling outside this file.

Research relevance:
- Provides legacy LAN Manager/RAP discovery compatibility for CIFS clients.
