# sources/user-network-fs/rclone/lib/encoder/filename/init.go

Source read signal: reviewed complete local file (101 lines, sha256 fc495bf7a5a2cf34).

Purpose: Owns filename compression table ids, URL table character mapping, once-only initialization, and runtime encoder/decoder tables.

Important APIs/types/functions: Defines `encodeURL`, `decodeMap`, `maxLength`, `initOnce`, `encTables`, `encTableLocks`, `decTables`, special table constants, `tablesData`, and `initCoders`.

Control flow: `initCoders` populates `decodeMap`, decodes each non-empty base64 Huffman table, reads it with `huff0.ReadTable`, configures compression preferences, stores encoder scratch and decoder instances, then configures `tableCustom` with a reusable encoder and no fixed decoder.

State and persistence behavior: All state is process-local and initialized exactly once. Encoders are stateful and require per-table locks when used; decoders are treated as stateless except for custom decode scratch in `decode.go`.

Dependencies and integration points: Depends on `base64`, `sync`, and `huff0`. The data table is consumed by `EncodeBytes` and `DecodeBytes`, so table ids are an on-disk/on-remote compatibility surface.

Risks and test signals: Changing table ids or table bytes can break existing encoded filenames. Panics during init indicate invalid checked-in table data; tests should exercise every non-empty table and reserved/custom behavior.
