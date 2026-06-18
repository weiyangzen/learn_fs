# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/utf.c

UTF-8 and historical UTF-1 conversion support for `tcs`.

Key responsibilities:
- `utf_in()` reads byte streams, preserves incomplete tails between reads, validates UTF-8, and emits runes.
- `utf_out()` emits runes as UTF-8.
- `isoutf_in()` and `isoutf_out()` implement ISO 10646 Annex A UTF-1 style conversion.
- `isochartorune()`, `runetoisoutf()`, and `fullisorune()` implement UTF-1 decoding, encoding, and completeness checks.
- `our_wctomb()` and `our_mbtowc()` implement portable UTF-8 encode/decode without relying on platform `wchar_t`.

Important behavior:
- UTF-8 validation rejects bad continuation bytes and overlong encodings.
- Supports old 1 to 6 byte UTF-8 form, reflecting historical FSS-UTF rather than current Unicode scalar-value limits.
- Bad input increments `nerrors`; with `clean`, bad bytes are skipped.

Notable risks:
- Six-byte UTF-8 support is obsolete by modern UTF-8 rules.
- `utf_in()` counts consumed bytes, not necessarily total bytes read until tail handling completes.
- UTF-1 code is compatibility-oriented and assumes the historical encoding ranges and escape tables.
