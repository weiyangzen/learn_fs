# File Research: sources/os/linux/linux-stable/fs/smb/client/gen_smb2_mapping

## Summary
Perl generator for SMB2/NT status to POSIX error mapping rows. It reads annotated `#define` status constants, validates duplicate status names, sorts by numeric status code, merges adjacent synonyms with identical values, skips success status zero, and writes generated C table entries.

## Main Responsibilities
- Validate command-line usage as `<in-h-file> <out-c-file>`.
- Read status definitions from the input header.
- Match constants of the form `#define NAME cpu_to_le32(0x...) // -ERR`.
- Ignore `STATUS_SEVERITY*` helper definitions.
- Reject duplicate status macro names.
- Sort parsed statuses by numeric code.
- Merge same-code synonyms into a single display string joined by ` or `.
- Skip the zero status code.
- Emit `{ code, error, "status names" },` rows to the output file.

## Input And Output Format
The parser expects each mapping-worthy status definition to use `cpu_to_le32(...)` and a trailing `// -POSIX_ERROR` annotation. It stores the symbolic name, original hex string, numeric code, and POSIX-style error string.

The output file contains only table rows, not a full C translation unit. Each row uses the original code token, mapped error, and a human-readable status-name string. A padding variable is computed but not actually used in the final `print`, so formatting is simple and uniform.

## Dependencies And Invariants
The generated mapping depends on header annotations being exact. The script assumes synonyms become adjacent after numeric sorting and that the table consumer expects CPU-endian ascending status codes. Output mode is not specialized by filename; any output path receives the same SMB2 mapping row format.

## Risks
Unannotated status definitions are silently ignored. Comment-format drift can remove mappings without an explicit error unless the line no longer matches at all. The output file is written directly, so interrupted generation can leave partial output. Duplicate numeric values are handled as synonyms, but duplicate names are fatal.
