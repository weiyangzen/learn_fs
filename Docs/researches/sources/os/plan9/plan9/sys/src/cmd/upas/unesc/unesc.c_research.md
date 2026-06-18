# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/unesc/unesc.c

Read fully: 52 lines, 969 bytes. SHA-256 prefix: `1f4bc2c8322c2f1c`.

This command decodes a narrow form of RFC2047-like encoded words from stdin to stdout. It copies ordinary bytes, detects `=?charset?encoding?encoded?=`, discards charset and encoding labels, and decodes `=HH` hex escapes inside the encoded section.

`hex()` maps hex digits to numeric values and returns zero for invalid input. `main()` streams with `Biobuf`, consumes encoded-word delimiters, and preserves malformed non-encoded `=` sequences as literal output.

Integration: standalone upas utility; likely used in mail-processing pipelines where encoded header fragments need simple unescaping.

Risk notes: it ignores the declared charset and encoding mode and only decodes quoted-printable-style `=HH`. It is not a complete RFC2047 decoder.
