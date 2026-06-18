# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/pictures.c

Purpose: Implements PostScript picture inclusion for `tr2post`.

Key behavior:
- `picture` parses `x X PI` colon-separated arguments: offsets, indent, line length, trap distance, file/page, frame dimensions, and flags.
- Supports centering/justification, outline, whiteout, scale-both, and rotation flags.
- Opens the referenced picture and calls `ps_include` to place it in the current page coordinate system.
- Temporarily restores/saves the surrounding PostScript state around inclusion.
- `picopen` currently opens the path directly.
- `piccopy` copies a fixed byte count between `Biobufhdr`s.
- Inline-picture support is present only inside disabled `#ifdef UNDEF` blocks.

Dependencies and integration:
- Called from `devcntl.c`.
- Uses `ps_include.c`, current troff position, device resolution, and page selection state.

Risks and notes:
- Argument count checks are off by one: code uses `fields[6]` and sometimes `fields[7]`.
- Inline-picture comments describe a larger design that is not active.
- `picopen` fatal-errors on missing files despite caller also checking for NULL.
