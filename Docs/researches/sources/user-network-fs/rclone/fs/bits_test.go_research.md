# sources/user-network-fs/rclone/fs/bits_test.go

Purpose: tests the generic `Bits` option type using a local `bitsChoices` implementation with `OFF`, `A`, `B`, and `C`.

Important APIs/functions: the test declares `type bits = Bits[bitsChoices]` and constants `bitA`, `bitB`, `bitC`. It asserts `bits` implements `Flagger` and `FlaggerNP`. `TestBitsString`, `TestBitsHelp`, `TestBitsSet`, `TestBitsIsSet`, `TestBitsType`, `TestBitsScan`, `TestBitsUnmarshallJSON`, and `TestBitsMarshalJSON` cover the exposed behavior.

Control flow: parse tests initialize a value to all bits set, call `Set` or `json.Unmarshal`, and assert successful parses assign the wanted value while failed parses leave the original value unchanged. JSON tests cover quoted strings and numeric literals.

State and persistence behavior: test data documents that zero renders as `OFF`, unknown residual bits render as `Unknown-0x...`, and JSON marshaling persists string names rather than integers.

Dependencies and integration points: uses `encoding/json`, `fmt.Sscan`, `strconv`, and `testify`. It anchors behavior required by CLI/config flag parsing.

Risks: no test covers a choices type with no zero option, duplicate choice names, custom `Type`, or overlapping bit masks.

Test signals: strong table coverage for normal parsing, invalid choice errors, JSON compatibility, and interface satisfaction.
