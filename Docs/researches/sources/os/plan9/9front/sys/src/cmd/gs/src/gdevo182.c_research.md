# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevo182.c

## Role

Okidata Microline 182 dot-matrix printer driver.

## Exported Device

- `gs_oki182_device`, named `oki182`, 1-bit output, default 72x72 DPI, 8x11 inch page.

## Main Helpers

- `oki_transpose` converts seven scan lines into Okidata column bytes. Each byte encodes a 7-pixel vertical column with the high bit set to avoid accidental command bytes.
- `oki_compress` trims trailing blank columns and replaces leading blank columns with spaces where possible.

## Print Flow

`oki_print_page`:

1. Allocates input and output buffers.
2. Sends printer initialization commands.
3. Supports normal and high-resolution mode.
4. Skips blank scan lines with fine line-feed commands.
5. Reads blocks of 7 or 14 scan lines.
6. Transposes and compresses graphics data.
7. Emits graphics command/data sequences and form-feed at end.
8. Frees buffers.

## Risks and Edge Cases

- Device command sequences are hard-coded and depend on printer DIP-switch/config assumptions documented in comments.
- Compression only trims leading/trailing blanks; embedded blank runs are not optimized.
- Uses raw control characters in stream output.
