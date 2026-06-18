# File Research: sources/virtualization/guestfs-tools/builder/index-validate.c

## Scope

Standalone C validator for virt-builder index files.

## CLI And Behavior

- Accepts one index file plus `--version`, `--help`, and compatibility flags `--compat-1.24.0` / `--compat-1.24.1`.
- Parses the file through the shared flex/bison parser.
- Reports parse failures as validation errors after closing input.
- Under `--compat-1.24.1`, rejects indexes containing comments.
- Under `--compat-1.24.0`, rejects section names with underscores and requires every section to contain `sig`.
- Under `--compat-1.24.1`, rejects field keys containing `.` or `,`.
- Prints `<input> validated OK` on success.

## Dependencies And Risks

- Shares parser structures with OCaml builder code.
- Compatibility checks are semantic post-parse checks, not scanner-level restrictions.
- Close errors are reported but ignored after parsing.
