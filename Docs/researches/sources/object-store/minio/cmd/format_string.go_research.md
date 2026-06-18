<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/format_string.go -->
# sources/object-store/minio/cmd/format_string.go

## Purpose
Generated `stringer` output for the `format` enum from `untar.go`. It converts compression/archive format constants into stable human-readable strings.

## Important APIs, types, and functions
- Compile-time index checks in `_()` ensure enum values still match generated ordering.
- `_format_name` and `_format_index` encode names for `Unknown`, `Gzip`, `Zstd`, `LZ4`, `S2`, and `BZ2`.
- `(format).String()` returns the enum name or `format(<n>)` for out-of-range values.

## Control flow
The string method bounds-checks the enum and slices the generated name table by index offsets. Invalid values are formatted with `strconv.FormatInt`.

## State and persistence behavior
No runtime or persistent state. It is generated code and should be regenerated rather than manually edited when enum constants change.

## Dependencies and integration points
Used wherever MinIO displays or logs the `format` enum. The file depends only on `strconv` and enum constants defined elsewhere.

## Risks and edge cases
Manual edits can desynchronize constants and strings. The compile-time array-index checks catch changed numeric constants during build.

## Test signals
No direct tests in this group; build success is the primary signal that generated constants match enum values.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/format_string.go -->
