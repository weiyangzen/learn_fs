# sources/user-network-fs/rclone/fs/metadata_mapper_code.go

## Purpose
`metadata_mapper_code.go` is a build-ignored helper program used by `metadata_test.go` to exercise the external metadata mapper protocol.

## Important APIs, types, and functions
The program defines a generic `check` helper and `main`. It reads JSON from stdin into `map[string]any`, validates selected fields, transforms `Metadata`, and writes a JSON object containing mapped metadata.

## Control flow
`main` decodes input, requires `Metadata`, checks expected `Size`, `SrcFs`, `SrcFsType`, `DstFs`, `DstFsType`, `Remote`, `MimeType`, `ModTime`, and `IsDir`, then iterates metadata. Key `error` triggers stderr output and exit status 1; `key1` is prefixed with `two `; `key3` is dropped; `key0=cabbage` is added. Output is JSON-encoded on stdout.

## State and persistence behavior
The helper has no persistent state. It communicates only through stdin/stdout/stderr and process exit code.

## Dependencies and integration points
It is invoked by `go run metadata_mapper_code.go` from tests through `fs.MetadataMapper`. It defines the expected JSON shape produced by `metadata.go`'s mapper path.

## Risks and edge cases
The helper uses type assertions against `any` values, so mismatched JSON types panic or exit. It checks exact strings and float size representation, making it sensitive to mapper contract changes. The final `if err != nil` after encoding is stale because `err` was not reassigned from `Encode`.

## Test signals
Although not part of normal builds, it is central to `TestMetadataMapper`: successful transformation, error propagation, and metadata-option override behavior all run through this helper.

Source-read signal: reviewed complete local file (74 lines). Functions/methods observed: `check`, `main`.
