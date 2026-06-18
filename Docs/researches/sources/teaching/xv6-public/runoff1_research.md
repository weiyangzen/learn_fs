# File Research: sources/teaching/xv6-public/runoff1

Perl source formatter used by `runoff`.

Behavior:
- Accepts optional verbose mode and starting line number via `-n`.
- Reads one source file from stdin/argument context, trims trailing whitespace, and warns about lines >= 75 chars.
- Emits numbered 50-line pages.
- Honors `PAGEBREAK!` and `PAGEBREAK: N` markers and otherwise chooses page breaks near blanks/function boundaries.
- Pads pages with numbered blank lines.

Role:
- Prepares stable, page-aligned source listings for the xv6 book/handout pipeline.
