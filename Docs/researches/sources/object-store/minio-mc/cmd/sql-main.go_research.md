# sources/object-store/minio-mc/cmd/sql-main.go

## Purpose
Implements `mc sql`, running S3 Select SQL expressions against objects or recursively against supported content types under a prefix.

## Important APIs, types, and functions
- `sqlFlags` covers query, recursive mode, CSV/JSON input and output serialization, compression, and optional CSV output headers.
- Valid key lists and abbreviation maps define accepted serialization options.
- `parseKVArgs` parses comma-delimited `key=value` options with escape replacement for `\n`, `\t`, and `\r`.
- `parseSerializationOpts` expands abbreviations and validates keys.
- `getInputSerializationOpts`, `getOutputSerializationOpts`, and `getSQLOpts` build `SelectObjectOpts`.
- `getCSVHeader`, `isSelectAll`, and `getCSVOutputHeaders` infer or use CSV output headers.
- `sqlSelect` runs `Client.Select` and copies result to stdout.
- `validateOpts` rejects CSV/JSON input flags for `.parquet`.
- `mainSQL` coordinates validation, stat/list traversal, and selection.

## Control flow
The command parses encryption keys and requires at least one target. For each target it stats the URL. File targets build query/options once for the first output header and call `sqlSelect`. Directory targets create a client and list with `Recursive` and metadata enabled, choose content type from extension or user metadata, and run select only for supported content type suffixes. CSV headers are written only once across the whole invocation.

Serialization parsing rejects simultaneous CSV/JSON input or output modes, rejects JSON output combined with CSV headers, and normalizes keys to lowercase long names.

## State and persistence
Read-only remote object access plus stdout streaming. No local or remote persistence. Uses encryption keys provided for command execution only.

## Dependencies and integration points
Uses S3 Select through the client abstraction, `SelectObjectOpts`, encryption-key helpers, `url2Stat`, object stream metadata helpers, gzip/bzip2 readers for header inference, MIME DB, global JSON flag, and global output/error helpers.

## Risks and edge cases
- `parseKVArgs` has custom comma parsing and can be sensitive to values containing comma-like sequences.
- Header inference reads the first line of the source object/stdin; for stdin this consumes input before selection.
- In recursive mode, `writeHdr` is set false inside the content-type suffix loop, which means unsupported first objects can still suppress headers.
- `sqlSelect` writes raw result bytes to stdout, bypassing the normal message system.
- Directory traversal silently skips unsupported content types.

## Test signals
`sql-main_test.go` covers `parseKVArgs` and `parseSerializationOpts` including duplicate keys, abbreviation expansion, invalid keys, case-insensitive long keys, and JSON input type parsing. More coverage is needed for recursive flow, header inference, parquet validation, and select invocation.
