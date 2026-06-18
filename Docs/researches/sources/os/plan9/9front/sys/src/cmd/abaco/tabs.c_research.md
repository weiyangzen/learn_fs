# File Research: sources/os/plan9/9front/sys/src/cmd/abaco/tabs.c

HTML table sizing, layout, and drawing support for Abaco.

Key responsibilities:
- Draws table backgrounds, borders, cells, and nested cell layouts.
- Computes per-cell min/max widths by laying out content with narrow and wide constraints.
- Computes column widths from cell constraints, colspan, specified dimensions, and available width.
- Computes row heights from cell content, rowspan, and specified heights.
- Computes total table width/height including border, padding, and spacing.
- Lays table cells into final rectangles with nested `Lay` objects.

Important behavior:
- `settables()` marks top-level table items and precomputes table constraints for all document tables.
- Colspan/rowspan of zero extends to the remaining columns/rows.
- Width distribution interpolates between min and max widths when max width exceeds available space.
- Top-level table width can expand to fill available width when specified.

Dependencies:
- Uses libhtml `Table`, `Tablecell`, `Itable`, `Dimen`, and Abaco `layitems()`.

Notable risks:
- Table layout is O(cells * repeated layout passes), which can be expensive for large/nested tables.
- Several arrays are allocated from `t->ncol`; malformed table metadata would be hazardous.
