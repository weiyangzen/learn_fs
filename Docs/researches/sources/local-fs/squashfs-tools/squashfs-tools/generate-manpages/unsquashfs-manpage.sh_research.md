# File Research: sources/local-fs/squashfs-tools/squashfs-tools/generate-manpages/unsquashfs-manpage.sh

Generates an `unsquashfs(1)` manpage from live `unsquashfs -help-all` and `-version` output using `help2man`.

Workflow:
- Must run from `generate-manpages`.
- Requires GNU sed and `help2man`.
- Validates executable `unsquashfs`.
- Captures help/version output to a temp directory.
- Creates a wrapper executable for `help2man`.
- Normalizes version/copyright/author.
- Edits help output into manpage-friendly formatting.
- Runs `help2man -Ni unsquashfs.h2m`.

Transformations:
- Converts `SYNTAX:` to `Usage:`.
- Inserts `*OPTIONS*`.
- Splits bracketed short/long option forms.
- Converts tabs to option/description spacing.
- Uppercases and removes operand angle brackets.
- Concatenates decompressor list, option text, exit-status text, `PAGER`, and `SQFS_CMDLINE`.
- Sectionizes Decompressors available, Exit status, See also, and Environment.
- Adds See Also references to `mksquashfs(1)`, `sqfstar(1)`, and `sqfscat(1)`.

Notable quirks:
- Temp cleanup is only on success.
- Formatting edits are tightly coupled to generated help text.
