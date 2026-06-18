# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/text2post/text2post.c

Purpose: Converts plain text/UTF input into structured PostScript pages.

Key behavior:
- Emits DSC header, `postprint` prologue, optional round-page support, encoding, setup, form-per-page support, unknown-character prologue, trailer, fonts, and page count.
- Maintains page, line, character, spacing, tab, and PostScript string state.
- `txt2post` reads runes; high byte selects a Lucida Unicode font bank, low byte selects glyph.
- Handles spaces, tabs, newlines, formfeeds, and backspaces.
- `pagelist` builds a bitmap of selected output pages from ranges.
- Tracks used fonts for the final `DocumentFonts` trailer.

Dependencies and integration:
- Uses Plan 9 `Bio`, `comments.h`, `path.h`, common prologue files, and `/sys/lib/postscript/prologues/pjw.char.ps`.
- Closely follows other Plan 9 PostScript tool setup options.

Risks and notes:
- `pagelist` reallocates without zeroing newly allocated bytes, so page bitmap expansion may inherit garbage bits.
- Unsupported/out-of-range font banks emit `pw`.
- Backspace behavior is partial and mainly moves by previous character width.
