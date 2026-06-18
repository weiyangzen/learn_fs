# File Research: sources/os/linux/linux/fs/smb/client/gen_smb1_mapping

## Role

Perl generator for SMB1 error mapping C tables.

## Behavior

- Expects exactly two arguments: input header and output C file.
- Supports two input formats:
  - `nterr.h`: parses `NT_STATUS_*` defines with mapping comments containing status class and code.
  - `smberr.h`: parses `ERR*`/`Err*` defines with POSIX error comments and tracks the current error class from header comments.
- Handles backslash line continuations before matching.
- Rejects commented mapping defines that do not match the expected annotation format.
- Deduplicates NT status macro names.
- Converts numeric expressions by removing whitespace/parentheses and OR-ing hex components for NT status values.
- Fails if no mapping entries are found.
- Sorts entries numerically by value before output.

## Outputs

- `smb1_mapping_table.c`: emits NT status to DOS class/code mappings with synonym macro names merged into one string when values match.
- `smb1_err_dos_map.c`: emits SMB1 DOS-class error to POSIX error mappings.
- `smb1_err_srv_map.c`: emits SMB1 server-class error to POSIX error mappings.
- Any other output filename is rejected.

## Dependencies

Uses only core Perl facilities. The generator relies on strict source-comment conventions in CIFS headers.

## Research Notes

The script intentionally treats malformed annotated comments as build-time errors. This keeps generated mapping tables synchronized with the semantic annotations in `nterr.h` and `smberr.h`.
