# File Research: sources/os/plan9/9front/sys/src/cmd/aux/aout2uimage.c

Role: Converts Plan 9 a.out images into U-Boot `uImage` format.

Main behavior:
- Parses `-o outfile`, `-Z kzero`, and `-l ostype` options; default OS type is Plan 9 (`23`), default `kzero` is `0xF0000000`.
- Uses `<mach.h>` to map Plan 9 machine types to U-Boot architecture IDs.
- Writes a placeholder 64-byte header, copies text and data, then seeks back to write the real header.
- Rounds text size out to a machine page boundary before data, matching Plan 9 reboot image expectations.
- Computes CRC32 for image payload and header using `<flate.h>` helpers.

Key helpers:
- `put` writes big-endian 32-bit header fields.
- `block` copies a fixed block and updates data CRC.
- `copy` streams a requested byte count in buffer-sized chunks.

Output:
- Defaults to `<input basename>.u`.
- Produces uncompressed type-2 kernel images with load and entry addresses relative to `kzero`.
