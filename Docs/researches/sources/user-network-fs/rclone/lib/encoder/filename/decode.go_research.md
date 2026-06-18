# sources/user-network-fs/rclone/lib/encoder/filename/decode.go

Source read signal: reviewed complete local file (95 lines, sha256 c75c5a9244ebd972).

Purpose: Decodes compact URL-safe filename encodings produced by the sibling encoder, including uncompressed, SCSU, run-length, predefined Huffman, and custom Huffman-table payloads.

Important APIs/types/functions: Exports `ErrCorrupted`, `ErrUnsupported`, `Decode`, and `DecodeBytes`. Package state includes `customDec` plus `customDecMu` because `huff0.Scratch` is stateful.

Control flow: `Decode` initializes coders, validates the leading table character through `decodeMap`, base64 URL-decodes the remaining payload, then delegates to `DecodeBytes`. `DecodeBytes` switches on the table id: raw bytes return directly, reserved ids report future-version unsupported, SCSU tables call `scsu.Decode`, RLE parses a uvarint count and repeated byte, custom tables read an embedded Huffman table under lock, and predefined tables use `decTables`.

State and persistence behavior: Decoder tables are initialized once by `initCoders`; custom Huffman decode reuses protected scratch memory. No durable state is written.

Dependencies and integration points: Uses `encoding/base64`, `encoding/binary`, `bytes`, `sync`, `scsu`, and `klauspost/compress/huff0`. It is the inverse of `filename.Encode` and is used anywhere rclone needs reversible URL-safe compressed filenames.

Risks and test signals: Corruption handling depends on strict table bounds, base64 validity, uvarint length, `maxLength`, and Huffman errors. Concurrency risk is isolated to the custom decoder lock; tests and fuzzing should continue to cover malformed inputs and all table classes.
