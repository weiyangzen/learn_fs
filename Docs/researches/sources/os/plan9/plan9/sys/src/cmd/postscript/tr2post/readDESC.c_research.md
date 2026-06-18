# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/readDESC.c

Purpose: Reads troff device `DESC` metadata for `tr2post`.

Key behavior:
- Builds the path `%s/dev%s/DESC` from `FONTDIR` and `devname`.
- Recognizes tokens: `PDL`, `Encoding`, `fonts`, `sizes`, `res`, `hor`, `vert`, `unitwidth`, `charset`.
- Stores print description language, encoding, device resolution, unit width.
- Allocates and initializes mounted-font table based on `fonts`.
- Mounts listed fonts and forces metric/font-map loading with `findtfn`.
- Ignores sizes, horizontal/vertical motion resolution, and special charset list.

Dependencies and integration:
- Called early in `tr2post.c`.
- Drives font and resolution state used by glyph output and drawing.

Risks and notes:
- Returns `0` at end even after successful parsing; caller ignores the value.
- Unknown tokens produce warnings unless comment lines.
- Uses global `fontmnt` state to distinguish font count from later font names.
