# sources/user-network-fs/rclone/lib/encoder/filename/encode.go

Source read signal: reviewed complete local file (85 lines, sha256 fc5f35a1605e4299).

Purpose: Encodes arbitrary byte strings into compact URL-safe filename strings by choosing the smallest available representation.

Important APIs/types/functions: Exports `Encode` and `EncodeBytes`. It uses package tables from `init.go`, SCSU transcoding, `huff0.Compress1X`, RLE fallback, and URL-safe base64.

Control flow: `EncodeBytes` initializes coders, starts with raw bytes as the current best, then walks each configured Huffman table for inputs of length 2 through `maxLength`. For `tableSCSU`, it first tries SCSU and records plain SCSU if smaller. It locks the stateful Huffman scratch for each table, records smaller compressed output, and handles `huff0.ErrUseRLE` by emitting a uvarint count plus repeated byte.

State and persistence behavior: Uses shared table scratch objects protected by `encTableLocks`; no persistent storage is modified. Returned payload slices are built from local copies of the original bytes.

Dependencies and integration points: Depends on `base64`, `binary`, `scsu`, and `huff0`. Its first-character table id is decoded by `Decode`, and the URL-safe output is suitable for remotes that need restricted path components.

Risks and test signals: The algorithm is size-driven, so table ordering and `WantLogLess` affect compatibility/performance. Inputs longer than 256 bytes or length 0/1 bypass compression; repeated-byte RLE must not be emitted for SCSU-transformed data.
