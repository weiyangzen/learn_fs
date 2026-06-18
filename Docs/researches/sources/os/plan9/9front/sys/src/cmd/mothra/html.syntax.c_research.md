# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/html.syntax.c

Defines the HTML tag syntax/action table for Mothra.

Key behavior:
- Populates `tag[]` entries mapping tag enum values to lowercase tag names and end-tag policy.
- Marks tags as `END`, `NOEND`, `OPTEND`, or `ERR`.
- Includes older and newer tags, including media tags and table/form elements.

Important dependencies: `html.h` tag enum values.

Notable risks:
- The designated initializers depend on tag enum stability.
- Several HTML optional-end tags are treated as `NOEND` or `END` based on Mothra’s simplified parser behavior.
