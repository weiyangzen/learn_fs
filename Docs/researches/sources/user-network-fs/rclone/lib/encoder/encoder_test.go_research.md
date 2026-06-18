# sources/user-network-fs/rclone/lib/encoder/encoder_test.go

Source read signal: reviewed complete local file (433 lines, sha256 96a87f5e45a09e9b).

Purpose: Exercises the `encoder.MultiEncoder` public contract: flag string parsing, generated encode/decode fixtures, invalid UTF-8 quoting, edge-only rules for dot/space/tilde/control characters, and benchmarks against older map-based replacement helpers.

Important APIs/types/functions: Compile-time assertions verify `MultiEncoder` implements `pflag.Value` and `fmt.Scanner`. `TestEncodeString`, `TestEncodeSet`, `TestEncodeSingleMask`, `TestEncodeSingleMaskEdge`, `TestEncodeDoubleMaskEdge`, `TestEncodeInvalidUnicode`, `TestEncodeDot`, and `TestDecodeHalf` cover user-visible behavior. Local `testCase`, `benchReplace`, `benchRestore`, `replaceReservedChars`, and `restoreReservedChars` support tests and benchmarks.

Control flow: Table-driven tests iterate generated fixtures from `encoder_cases_test.go`, encode each input, compare the expected output, then decode back to the original input. Invalid UTF-8 tests verify quote-rune byte escaping only when the relevant flag is set. Benchmarks compare the current encoder against legacy regex/map behavior for a OneDrive-like mask.

State and persistence behavior: The test file has no persistent state; it builds an inverse character map in `init()` for the legacy benchmark helpers. It depends on generated fixture data and on package globals from the encoder implementation.

Dependencies and integration points: Uses `testing`, `strconv`, `regexp`, `strings`, `pflag`, and `testify/assert`. It integrates with generated encoder cases and protects backend path encodings that rely on `MultiEncoder` flag combinations.

Risks and test signals: The tests are broad but depend on generated cases remaining synchronized with encoder flags. Edge cases include ambiguous quote-rune decoding, invalid UTF-8 byte preservation, only-left/right transforms, and unknown high-bit mask string formatting.
