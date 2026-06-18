# File Research: sources/teaching/xv6-public/runoff

Shell script for generating xv6 printable/PDF source output.

Key behavior:
- Creates numbered formatted source files with `runoff1`.
- Builds table of contents data and validates requested even/odd/left/right alignment from `runoff.spec`.
- Extracts definitions and cross-references from formatted source.
- Uses `pr.pl`, `pr`, `mpage`, optional LucidaSans-Typewriter font, and `ps2pdf` to create `xv6.pdf`.
- Handles README, table of contents, cross-references, blank pages, and all listed source files.

Role:
- Documentation publishing tool, not part of xv6 runtime.
