
# sources/security-integrity/ima-evm-utils/src/utils.c

## Purpose
`utils.c` provides small utility routines shared by TPM and CLI code: executable lookup in `PATH`, single-hex-character conversion, and hex-string-to-binary decoding.

## Important APIs, Types, And Functions
`get_cmd_path()` scans `$PATH` and writes the first readable regular-file match for a program into a caller buffer. `hex_to_bin()` maps ASCII hex digits to nibbles. `hex2bin()` decodes a requested number of bytes from hex text into a destination buffer, skipping single spaces between bytes.

## Control Flow
`get_cmd_path()` iterates colon-separated path elements, expanding empty elements to `.`, appending the program name with a slash if needed, and returning once `file_exist()` confirms readability and regular-file type. `hex2bin()` loops over `count` bytes and stops with `-1` on invalid nibbles.

## State And Persistence
The file is stateless. It reads environment state via `PATH` and filesystem metadata through `access()`/`stat()`.

## Dependencies And Integration Points
`pcr_tsspcrread.c` uses `get_cmd_path()`. `evmctl.c` and TPM backends use `hex2bin()` for PCR files, UUID/xattr parsing, and command output conversion.

## Risks
`get_cmd_path()` uses readable regular files rather than executability, so it may accept non-executable files. It relies on careful buffer-length checks around `snprintf()`. `hex2bin()` does not skip arbitrary whitespace and assumes the caller provides enough source characters and destination space.

## Test Signals
Coverage is indirect through PCR command lookup, PCR file parsing, hash/sign input parsing, and xattr override tests.
