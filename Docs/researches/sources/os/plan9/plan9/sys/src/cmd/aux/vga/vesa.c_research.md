# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/vesa.c

VESA BIOS Extension and EDID support for Plan 9 `aux/vga`.

Key behavior:
- Opens `/dev/realmode` and `/dev/realmodemem`, stages BIOS call buffers at physical `0x9000`, and invokes interrupt `0x10`.
- Validates VBE 2+ signature and builds a VESA-backed `Ctlr` chain with software cursor.
- Enumerates VBE modes, queries mode info, constructs Plan 9 mode names/channels, and scans unoffered mode IDs if necessary.
- Sets VBE graphics modes using linear framebuffer and no-clear flags.
- Dumps VBE info, mode list, unoffered modes, and EDID.
- Parses EDID 128-byte blocks:
  - manufacturer/product/serial/date/version,
  - display flags,
  - established timings,
  - standard timing IDs,
  - detailed timing blocks,
  - monitor descriptor blocks for serial/name/range limits.
- Converts EDID timing data to `Mode` entries and deduplicates by generated mode name.
- Uses `vesadb.c`’s `vesamodes[]` for standard timing lookup.

Important details:
- `Vmode.chan` is derived from VBE RGB masks for direct-color modes.
- `dbvesamode()` creates a minimal Plan 9 `Mode` with attribute `id=0x...`.
- EDID parsing currently includes debug output calls (`fprint(2, "dt\n")`, hex dumps, and `print("fd ...")`).
- `vesatextmode()` switches back to mode 3 through VBE.

Filesystem relevance:
- Mostly indirect. It interacts with Plan 9 device files for real-mode BIOS access but does not implement filesystem behavior.
