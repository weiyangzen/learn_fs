# File Research: sources/local-fs/squashfs-tools/squashfs-tools/generate-manpages/sqfstar-manpage.sh

Generates a `sqfstar(1)` manpage from live `sqfstar -help-all` and `-version` output.

Workflow:
- Must run from `generate-manpages`.
- Requires GNU sed, `expand`, and `help2man`.
- Validates executable `sqfstar`.
- Captures expanded help and version output.
- Creates a temp wrapper script for `help2man`.
- Uses `sqfstar.h2m` to supply replacement front matter.
- Removes temp directory after successful generation.

Transformations:
- Joins wrapped first syntax line, inserts `*OPTIONS*`, then deletes original first line because `sqfstar.h2m` supplies that content.
- Indents options and compressor options.
- Adds spacing for long option descriptions.
- Uppercases operands, then restores quoted pseudo-definition forms where case matters.
- Concatenates compressor and LZO algorithm lists.
- Converts pseudo file definitions into option-like lines.
- Sectionizes compressor options, pseudo definition format, exit status, see also, environment, and symbolic mode specification.
- Adds See Also references to `mksquashfs(1)`, `unsquashfs(1)`, and `sqfscat(1)`.

Notable quirks:
- Performs both global angle-bracket removal and a later targeted removal expression, making the second mostly redundant.
- Depends closely on current help text shape.
