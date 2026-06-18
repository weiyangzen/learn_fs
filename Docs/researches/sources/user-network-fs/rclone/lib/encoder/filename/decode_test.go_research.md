# sources/user-network-fs/rclone/lib/encoder/filename/decode_test.go

Source read signal: reviewed complete local file (147 lines, sha256 fda102fbdb3bd610).

Purpose: Regression-tests decoding of stored compressed filename samples across all supported table classes and checks encode-size regressions.

Important APIs/types/functions: `TestDecode` drives fixtures with `name`, `encoded`, `want`, and `wantErr` fields, calling both `Decode` and `Encode`.

Control flow: Each fixture decodes a known encoded string, compares errors and decoded text, then re-encodes the expected filename and flags any generated encoding longer than the checked-in reference.

State and persistence behavior: No persistent state is used beyond package decoder initialization. The test reads hard-coded payloads representing compatibility data.

Dependencies and integration points: Depends on the package encoder/decoder, predefined Huffman tables, SCSU support, and Go's testing package. It protects compatibility with previously generated filenames from older rclone versions.

Risks and test signals: The test covers raw, long raw, several fixed Huffman tables, custom Huffman, RLE, regular ASCII, and Unicode/SCSU examples. The duplicate `len(proposed) > len(tt.encoded)` branch logs the improvement path only after the same condition already failed, which limits the intended positive diagnostic.
