# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevhl7x.c

## Role
`gdevhl7x.c` implements a Brother HL-720/HL-730 family GDI printer driver, exposed as `hl7x0`.

## Device and Data Structures
- Defines `ByteList` as a bounded byte buffer writer and `Summary` for previous-line data, blank-line count, sent-line count, page dimensions, horizontal offset, and resolution.
- `gs_hl7x0_device` uses custom open/close procs and `hl720_print_page`.
- `hl7x0_open` chooses A4 or letter margins using PCL paper-size detection, then opens the printer buffer.
- `hl7x0_close` opens the physical printer output and sends `@N@N@N@N@X`.

## Print Path
- `hl720_print_page` builds PJL/HBP initialization bytes and embeds a resolution-derived byte.
- `hl7x0_print_page` allocates a command buffer plus line buffer, emits initialization on the first page, repeatedly calls `dumpPage` until the page is consumed, then sends a form feed command.
- `dumpPage` copies scanlines, strips trailing zero bytes, accumulates blank lines as `0xff`, emits `@G` command headers with 3-byte sizes, and splits output when the command buffer fills.
- `makeFullLine` compares current and previous lines by XOR and converts changed byte sequences into commands. A compile-time `USE_POSSIBLY_FLAWED_COMPRESSION` block can skip unchanged regions, but the default disables that line-to-line compression due to documented printer artifacts.
- `makeCommandsForSequence` splits byte sequences into repeated and non-repeated runs, using `makeSequenceWithRepeat` and `makeSequenceWithoutRepeat`.
- `addCodedNumber` encodes long offsets/lengths using repeated `0xff` bytes plus a remainder.

## Risks and Notes
- The file contains a likely build/maintenance issue: `hl7x0_print_page` frees `storage` with `storage_size_words`, but that identifier is not defined in this file. The allocation used `sizeOfBuffer + line_size` bytes, so this looks inconsistent unless supplied by an unusual macro elsewhere.
- `Summary.previousData` is fixed at 1500 bytes and assumes it exceeds any possible scanline width.
- Filesystem relevance is limited to streaming printer command data to `FILE *`; it also opens/closes the printer output in the device close path.
