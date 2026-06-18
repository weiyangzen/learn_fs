# File Research: sources/local-fs/squashfs-tools/squashfs-tools/generate-manpages/sqfscat-manpage.sh

Generates a `sqfscat(1)` manpage from live `sqfscat -help-all` and `-version` output using `help2man`.

Workflow:
- Requires running from `generate-manpages`.
- Requires GNU sed and `help2man`.
- Validates executable `sqfscat` under the supplied path.
- Captures help/version output, wraps it with a temporary script, edits it, then calls `help2man -Ni sqfscat.h2m`.
- Removes the temp directory after success.

Transformations:
- Converts `SYNTAX:` to `Usage:`.
- Inserts `*OPTIONS*`.
- Splits bracketed short/long option forms into explicit alternatives.
- Uppercases and removes angle brackets from operands.
- Concatenates decompressor list and multi-line option descriptions.
- Concatenates exit status, `PAGER`, and `SQFS_CMDLINE` text.
- Sectionizes Decompressors available, Exit status, See also, and Environment.
- Adds See Also references to `mksquashfs(1)`, `unsquashfs(1)`, and `sqfstar(1)`.

Notable quirk:
- Duplicate comment line for “Make Decompressors available header”.
