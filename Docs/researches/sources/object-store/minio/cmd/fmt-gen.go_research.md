<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/fmt-gen.go -->
# sources/object-store/minio/cmd/fmt-gen.go

## Purpose
Defines the hidden `fmt-gen` CLI command that generates a `format.json.zip` bundle for an erasure server pool without contacting drives. It is an operational tool for prebuilding per-drive format files.

## Important APIs, types, and functions
- `fmtGenFlags` accepts parity, deployment ID, and address flags.
- `fmtGenCmd` registers hidden command metadata, usage text, global flags, and `fmtGenMain`.
- `fmtGenMain` builds server context/endpoints, creates `format.json.zip`, generates `formatErasureV3` layouts per pool, and embeds one `format.json` per drive path.

## Control flow
The command parses common server arguments, creates endpoint pools, opens a zip writer, loops through each pool, creates a new erasure format matching set count and drives per set, optionally applies the requested deployment ID, clones the format for each drive with `Erasure.This` set to that drive's UUID, marshals JSON, and writes it under `host/path/.minio.sys/format.json` in the zip.

## State and persistence behavior
The only output is local `format.json.zip`. The generated JSON contains deployment ID, backend format, erasure version, distribution algorithm, set UUID matrix, and per-drive `This` UUID. It does not mutate actual storage endpoints.

## Dependencies and integration points
Depends on MinIO CLI, endpoint layout parsing, `newFormatErasureV3`, zip embedding helpers, and common server context initialization. It shares the format schema with startup and healing code in `format-erasure.go`.

## Risks and edge cases
Because output is topology-defining, endpoint parsing or drive order mistakes can generate unusable or dangerous format files. The `parity` flag is declared but not used directly in this file. Existing `format.json.zip` is overwritten by `os.Create`.

## Test signals
No direct tests in this group. Operational validation is that the zip contains one correctly addressed `format.json` per endpoint and that startup accepts the generated layout.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/fmt-gen.go -->
