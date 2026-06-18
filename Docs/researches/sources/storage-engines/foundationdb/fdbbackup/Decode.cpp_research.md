# sources/storage-engines/foundationdb/fdbbackup/Decode.cpp

## Purpose
Provides `decode_hex_string`, a utility for decoding escaped ASCII/hex strings into binary strings for backup decoder filters.

## Important APIs, Types, and Functions
`decode_hex_string(std::string line, bool& err)` handles `\xNN` hex escapes and simple escaped `"`, `\`, space, and `;`. It reports invalid syntax to stderr, sets `err`, and returns decoded content.

## Control Flow
The function scans and mutates `line` in place. Backslash dispatches to simple escape handling or two-digit hex parsing with `strtoul`; normal characters advance the index. The final result is `line.substr(0, i)`.

## State and Persistence Behavior
No persistent state. The caller owns the error flag. Diagnostics go to stderr.

## Dependencies and Integration Points
Declared by `fdbbackup/Decode.h` and used by `FileDecoder.cpp` for `--hex-prefix` and prefix-filter files.

## Risks
The loop condition `i <= line.length()` can inspect the string terminator, and bounds checks are delicate. `err` is not cleared on success. In-place mutation makes edge cases easy to miss.

## Test Signals
Test valid hex, escaped semicolons/backslashes/quotes/spaces, empty input, plain text, short escapes, invalid hex, and sanitizer runs for boundary behavior.
