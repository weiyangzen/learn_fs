# File Research: sources/os/linux/linux/fs/smb/client/gen_smb2_mapping

## Role

Perl generator for SMB2/SMB3 NT status to POSIX error mapping tables.

## Behavior

- Expects exactly two arguments: input header and output C file.
- Reads status defines matching `#define NAME cpu_to_le32(0x...) // -ERR`.
- Skips `STATUS_SEVERITY*` defines.
- Rejects duplicate status macro names.
- Stores each status macro, string code, numeric code, and POSIX error annotation.
- Sorts all entries by numeric NT status code.
- Skips numeric code zero during output.
- Merges adjacent synonyms with the same numeric status value into a single descriptive string using `or`.
- Emits C initializer rows of `{ code, error, "status names" },`.

## Dependencies

Uses only core Perl. It depends on SMB2 status headers using the exact `cpu_to_le32(...) // -ERR` annotation form.

## Research Notes

This is a compact build-time normalization step: source headers remain annotated with protocol constants, while generated C tables get sorted, synonym-merged entries suitable for lookup/debug output.
