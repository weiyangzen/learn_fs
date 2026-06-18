# sources/storage-engines/sqlite/ext/misc/totype.c

## Purpose
Implements `tointeger(X)` and `toreal(X)`, strict conversion helpers that return a converted value only when the input can be represented losslessly according to this extension's rules.

## Important APIs, Types, And Functions
Important helpers are `totypeAtoi64`, `totypeAtoF`, `totypeDoubleToInt`, endian macros, and constants for 64-bit integer bounds. SQL functions are `tointegerFunc` and `torealFunc`; `sqlite3_totype_init()` registers both as deterministic innocuous functions.

## Control Flow
`tointeger` accepts existing integers, floats exactly equal to their int64 cast, 8-byte little-endian integer blobs, and text parsed as an int64 with no extra characters. `toreal` accepts existing floats, integers that round-trip through double to int64, 8-byte big-endian IEEE754 blobs, and text parsed by the local floating-point parser with no leading/trailing whitespace or junk. Non-lossless cases return SQL NULL.

## State And Persistence Behavior
No state is stored. The functions only inspect input values and return converted values or NULL.

## Dependencies And Integration Points
Depends on SQLite scalar function APIs and local numeric parsing copied/adapted from SQLite internals. It is useful in tests or SQL that needs stricter conversion than SQLite's normal affinity rules.

## Risks And Edge Cases
Text parsing is intentionally strict and not identical to SQLite affinity conversion. Blob integer and real byte orders differ by design: little-endian for integer, big-endian for real. Floating-point edge handling includes infinities/underflow behavior from C doubles. Integer bounds around `9223372036854775808` require careful testing.

## Test Signals
Tests should cover every SQLite type, exact and inexact float-to-int cases, int-to-real precision loss, boundary int64 strings, invalid strings with whitespace/junk, zero and signed zero, exponent extremes, and endian-sensitive blob conversions.
