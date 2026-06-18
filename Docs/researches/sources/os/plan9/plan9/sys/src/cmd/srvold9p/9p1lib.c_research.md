# File Research: sources/os/plan9/plan9/sys/src/cmd/srvold9p/9p1lib.c

Serialization, deserialization, and formatting library for old 9P1 protocol records.

Key responsibilities:
- Formats `Fcall9p1` messages for diagnostics via `%G`.
- Converts `Fcall9p1` structs to/from 9P1 wire byte streams.
- Converts between modern `Dir` and fixed 9P1 directory records.
- Converts old auth ticket/authenticator records with optional DES encryption/decryption.

Important functions:
- `fcallfmt9p1`: readable per-message diagnostics.
- `convS2M9p1`: struct-to-wire conversion.
- `convM2S9p1`: wire-to-struct conversion with length validation.
- `convD2M9p1`/`convM2D9p1`: directory stat conversion.
- `convA2M9p1`, `convM2A9p1`, `convM2T9p1`: auth record conversion.
- `dumpsome`: prints data payload as printable text or hex.

Notable details:
- QTDIR is encoded in high bit of old qid path.
- 64-bit length/offset high words are skipped/zeroed where 9P1 only supports old widths.

Risks/quirks:
- Uses macros with direct byte pointer manipulation.
- Some string fields are copied fixed-width and may not be NUL-terminated.
