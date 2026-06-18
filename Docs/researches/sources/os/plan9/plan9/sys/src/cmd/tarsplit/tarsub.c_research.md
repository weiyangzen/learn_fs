# File Research: sources/os/plan9/plan9/sys/src/cmd/tarsplit/tarsub.c

Shared tar stream primitives for `tarcat` and `tarsplit`.

Key functions:
- `checksum` computes classic tar header checksum with the checksum field treated as spaces.
- `readtar` reads exact tar-block multiples and zero-fills a short final archive record.
- `getdir` reads one header, returns false on a zero header, validates checksum, stores member length, and updates `thisnm`/`lastnm`.
- `passtar` copies rounded file payload blocks unless the member is a link.
- `writetar` writes to output and tracks `outoff`.
- `closeout` writes two zero blocks and closes the archive.

Notable behavior:
- Size parsing uses octal-only `otoi`.
- Only hard/symbolic links are treated as no-payload entries; directories with nonzero sizes would be copied according to header length.
- `Blocksxfr = 32`, so payload copying uses 16 KiB chunks.
