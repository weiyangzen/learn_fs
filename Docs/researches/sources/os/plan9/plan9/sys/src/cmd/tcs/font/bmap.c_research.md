# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/font/bmap.c

Maps requested rune range to Big5 glyph ordinals.

Key function:
- `bmap(from, to, chars)` initializes output slots to zero, scans `tabbig5`, and records the Big5 ordinal for each rune in range.

Notable behavior:
- Reports how many requested characters were found and one missing rune if any are absent.
- Does not abort on missing mappings; the `exits("map problem")` call is commented out.
- A mapped ordinal of zero is indistinguishable from the initialized “missing” marker for rune equal to `tabbig5[0]`, but typical requested ranges likely avoid that ambiguity.
