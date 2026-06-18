# sources/storage-engines/sqlite/tool/varint.c

## Purpose
`varint.c` is a command-line converter between SQLite varint byte sequences and decimal integers.

## Important APIs, types, and functions
`hexValue()` parses one hex digit, `toHex()` formats a nibble, and `putVarint()` encodes a `u64` using SQLite's 1-to-9-byte varint representation. `main()` chooses decode mode when multiple arguments or a two-character hex byte is provided; otherwise it parses a signed or unsigned decimal and encodes it.

## Control flow
In hex-to-decimal mode, the program consumes up to 9 hex-byte arguments, accumulating seven payload bits per byte until a byte without the high bit appears, with the ninth byte contributing eight bits. In decimal-to-varint mode, it parses optional `+` or `-`, builds a `u64`, maps negative values through two's-complement representation, then calls `putVarint()` and prints decimal plus hex bytes.

## State and persistence behavior
No persistence. All conversion state is local variables and a 20-byte output buffer.

## Dependencies and integration points
It uses only standard C and is a developer/debugging helper for SQLite record/key encoding.

## Risks and edge cases
Decimal parsing does not detect overflow. Hex decode validates argument length but not that `hexValue()` returned nonnegative for both characters in every path, so invalid hex can produce nonsensical accumulation. Negative conversion depends on 8-byte `i64`/`u64` representation.

## Test signals
Known SQLite varint examples, 1-byte values, 9-byte max values, signed negative inputs, invalid hex bytes, extra arguments, and usage with no arguments are useful tests.
