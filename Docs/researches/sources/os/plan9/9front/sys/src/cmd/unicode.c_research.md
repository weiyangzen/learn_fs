# File Research: sources/os/plan9/9front/sys/src/cmd/unicode.c

This utility converts between Unicode code points and UTF text. Default mode prints UTF characters for hexadecimal code values. `-n` prints numeric code points for input UTF strings. `-t` emits characters without trailing newlines.

It also supports ranges like `0041-005a`, printing code point and character columns, eight per line. Input validation checks hex syntax, `Runemax`, and UTF round-trip validity for `Runeerror`.

Output uses Plan 9 `%C` rune formatting through a `Biobuf`.
