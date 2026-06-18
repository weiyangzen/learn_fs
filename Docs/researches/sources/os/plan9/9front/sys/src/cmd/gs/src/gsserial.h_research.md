# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsserial.h

Declares and macro-expands compact unsigned and signed integer encoders used by serialization code.

Key definitions:
- Unsigned values use base-128 little-endian bytes with bit 7 as the continuation flag.
- `enc_u_sizew`, `enc_u_size2w`, and point helpers provide fast size calculations.
- `enc_u_putw`, `enc_u_put2w`, `enc_u_getw`, and related macros inline one- and two-byte fast paths.
- Signed values use bit 6 of the first byte as the sign bit and bit 7 as continuation.
- `enc_s_putw`, `enc_s_getw`, and point helpers encode/decode signed integers with special handling for minimum int.

Dependencies:
- Requires Ghostscript base types and byte/point-compatible structures from included context.

Research notes:
- The header is intentionally macro-heavy for fast command-list style encoding.
- Comments contain minor typos, but the code path is clear and paired with the `UNIT_TEST` in `gsserial.c`.
