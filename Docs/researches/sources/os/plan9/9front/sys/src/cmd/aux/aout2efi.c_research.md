# File Research: sources/os/plan9/9front/sys/src/cmd/aux/aout2efi.c

Role: Converts a Plan 9 a.out kernel/image into a minimal PE/COFF EFI application image.

Main behavior:
- Parses options `-Z kzero` and `-o outfile`, then opens one a.out input.
- Uses `crackhdr` from `<mach.h>` to identify text/data sizes, entry address, header size, and machine type.
- Selects EFI machine IDs for i386, amd64, and arm64. i386 switches optional-header packing to 32-bit form; arm64 adds a dummy `.reloc` section.
- Builds a fixed 0x200-byte MZ plus PE header with one `.text` section, or `.reloc` plus `.text` for arm64.
- Copies the input image after the a.out header into the output after the EFI header.

Implementation details:
- `pack` serializes little-endian fields according to a compact format string (`b`, `w`, `l`, `q`, `0`), rewriting `q` to `l` in 32-bit mode.
- Output defaults to `<input basename>.efi`.

Risks and assumptions:
- The PE header is deliberately minimal; checksums, symbols, import tables, and relocation data are mostly unused.
- The code assumes the a.out payload is already suitable for EFI execution at the chosen `kzero`.
