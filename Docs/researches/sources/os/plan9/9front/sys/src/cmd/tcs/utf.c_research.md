# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/utf.c

`utf.c` supplies UTF-related converters for `tcs`: Plan 9 UTF-8, UTF-1/ISO 10646 Annex A, and Unicode normalization output.

Core functions:
- `utf_in()` reads bytes, preserves incomplete UTF sequences between reads, decodes with `our_mbtowc()`, and emits runes.
- `utf_out()` encodes runes with `our_wctomb()`.
- `utfnfc_out()` and `utfnfd_out()` wrap `utfnorm_out()` using Plan 9 normalization APIs.
- `isoutf_in()` and `isoutf_out()` implement UTF-1 input/output through `isochartorune()` and `runetoisoutf()`.
- `fullisorune()` determines whether enough bytes exist for a UTF-1 sequence.

Important implementation details:
- `our_wctomb()` supports historical UTF encodings up to 6 bytes.
- `our_mbtowc()` rejects bad continuation bytes and overlong encodings.
- `mktable()` builds translation tables for UTF-1 byte remapping.

Integration:
- Registered from `tcs.c` as `utf`, `utf-8`, `utf1`, `nfc`, and `nfd`.
- Uses global `runes`, `obuf`, counters, `squawk`, `clean`, and `nerrors` from the `tcs` program.

Risk notes:
- `utfnorm_out()` uses static normalization state, so it depends on the final zero-length flush call to finish a stream.
- UTF-8 handling accepts historical Plan 9 rune width behavior rather than modern strict Unicode scalar constraints.
