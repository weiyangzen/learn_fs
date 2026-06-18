# File Research: sources/local-fs/squashfs-tools/squashfs-tools/generate-manpages/mksquashfs-manpage.sh

Generates a `mksquashfs(1)` manpage from live `mksquashfs -help-all` and `-version` output using `help2man`.

Workflow:
- Must be run from `generate-manpages`.
- Requires GNU sed, `expand`, and `help2man`.
- Validates the supplied directory contains executable `mksquashfs`.
- Captures help and version output into a temp directory.
- Creates a temporary wrapper executable that serves modified help/version text to `help2man`.
- Normalizes version/copyright/author output.
- Rewrites help text into `help2man`-friendly sections and option layouts.
- Uses `mksquashfs.h2m` include file.
- Removes the temp directory after successful generation.

Transformations include:
- Converts `SYNTAX:` to `Usage:`.
- Inserts `*OPTIONS*`.
- Indents options for `help2man`.
- Expands shortened operands and uppercases manpage operands.
- Concatenates compressor lists and LZO algorithm lists.
- Turns compressor names and pseudo file format text into manpage sections.
- Adds See Also references to `unsquashfs(1)`, `sqfstar(1)`, and `sqfscat(1)`.
- Sectionizes Environment, Exit status, See also, and Symbolic mode specification.

Notable quirks:
- Temp cleanup is skipped on earlier failure exits.
- Heavily depends on exact `mksquashfs -help-all` formatting.
