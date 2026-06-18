# File Research: sources/os/plan9/9front/sys/src/cmd/pr.c

Plan 9 `pr` implementation: paginates files with headings, columns, line numbering, margins, tabs, optional multi-file columns, balancing, and odd-page padding.

Key behavior:
- `findopt` parses classic `pr` options such as columns, starting page, double spacing, tab handling, formfeed, headings, length, merge/across modes, offset, separator, width, numbering, balancing, and padding.
- `pr` opens a file/stdin, loops pages, prints headings from file mtime/current time, and calls `putpage`.
- `nexbuf` buffers page content for multi-column layout.
- `balance` redistributes final-page buffered lines.
- `get` abstracts reading from current file/column/buffer and updates input position.
- `put` and `putspace` emit output while respecting width, tabs, backspaces, and page filtering.

Integration points:
- Uses Plan 9 `Biobuf`, `Dir`, `dirstat`, `Bgetrune`, `Bputrune`.

Risks:
- Many globals encode formatter state; option interactions are subtle.
- Buffer size calculation multiplies by `sizeof(char)` before allocating `Rune` storage, resulting in larger-than-needed allocation rather than under-allocation on common builds.
- Deferred open errors are partially implemented via an error list type, but current `mustopen` prints directly rather than linking `Err` nodes.
