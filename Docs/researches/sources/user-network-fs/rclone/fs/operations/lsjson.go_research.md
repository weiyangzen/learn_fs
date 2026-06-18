# sources/user-network-fs/rclone/fs/operations/lsjson.go

## Purpose
`lsjson.go` converts filesystem directory entries into JSON-friendly listing records and implements recursive/non-recursive JSON list and stat operations.

## Important APIs, types, and functions
- `ListJSONItem` is the exported JSON record with path, name, encrypted names, size, MIME type, modtime, directory flags, hashes, IDs, tier, bucket marker, and metadata.
- `Timestamp.MarshalJSON` formats timestamps according to backend precision and emits `""` for zero time.
- `formatForPrecision` maps backend time precision to RFC3339-like formats.
- `ListJSONOpt` controls recursion, omitted fields, encrypted display, original IDs, hashes, file/dir filters, metadata, and selected hash types.
- `listJSON` stores resolved options, crypt cipher, hash types, and backend feature flags.
- `newListJSON`, `entry`, `ListJSON`, and `StatJSON` are the core constructors and listing/stat APIs.

## Control flow
`newListJSON` resolves file/dir inclusion mode, optionally loads crypt configuration and cipher for encrypted path display, captures backend precision and tier/bucket features, and normalizes requested hash types. `entry` filters files or directories, fills core fields, optionally reads modtime, MIME type, encrypted path, metadata, IDs, original IDs, hashes, tier, and bucket markers. `ListJSON` walks the tree with `walk.ListR` and calls a callback for every non-filtered item. `StatJSON` special-cases root, tries `NewObject` for file paths, then lists the parent directory to find directory entries or case-insensitive matches.

## State and persistence behavior
The file is read-only toward remotes. It may read object hashes, metadata, MIME type, tier, and directory listings. It stores only transient listing configuration and callback output.

## Dependencies and integration points
It depends on the `crypt` backend for encrypted name display, `fs` metadata/ID/tier interfaces, `accounting.Stats().Listed`, `hash`, `walk.ListR`, and shared `ConfigMaxDepth`. It is used by `lsjson`, `stat`, logger destination-after output, and list formatting.

## Risks and edge cases
Encrypted output only works for crypt remotes and requires loading the backend config. `FilesOnly` and `DirsOnly` both true intentionally means both are included. `StatJSON` lacks a direct generic `NewDirEntry` primitive, so directory stat falls back to parent listing and can be affected by backend case sensitivity or root existence semantics. Hash and metadata reads log errors but still return partial items.

## Test signals
`lsjson_test.go` covers default, files-only, dirs-only, recursive, subdirectory, no-modtime, no-mimetype, show-hash, explicit hash types, metadata, root stat, file stat, directory stat with trailing slash, not-found handling, and backend root error behavior.
