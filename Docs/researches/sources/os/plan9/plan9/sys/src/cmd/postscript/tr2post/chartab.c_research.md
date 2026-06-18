# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/chartab.c

Purpose: Manages troff font mounting, metric loading, glyph lookup tables, and PostScript font selection for `tr2post`.

Key behavior:
- `mountfont` updates the troff mounted-font table.
- `settrfont` resolves current troff font position to a loaded troff font entry.
- `setpsfont` emits PostScript font changes and optional slant/height changes.
- `findpfn` interns PostScript font names.
- `readpsfontdesc` reads `/sys/lib/postscript/troff/<font>` map ranges from Unicode/troff glyph ranges to PostScript font ranges.
- `readtroffmetric` reads `/sys/lib/troff/font/dev<devname>/<font>` metric files, charsets, widths, special flags, and named character entries.
- `findtfn` lazily loads troff metric and PostScript descriptions.
- `finish` writes trailer font and page metadata.
- `t_slant` and `t_charht` affect later `setpsfont` output.

Dependencies and integration:
- Core service used by `conv.c`, `utils.c`, `readDESC.c`, and prologue generation.
- Relies on `devname`, font directories, `galloc`, `Bgetfield`, and Plan 9 rune conventions.

Risks and notes:
- Many fatal paths for missing or inconsistent font metadata.
- Quote handling in metric charset entries is marked incomplete.
- Font descriptions must not cross 256-glyph block boundaries.
- Global font state is reset indirectly by changing `curpostfontid`.
