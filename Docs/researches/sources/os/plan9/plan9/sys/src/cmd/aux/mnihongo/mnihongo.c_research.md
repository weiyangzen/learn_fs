# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/mnihongo/mnihongo.c

This file post-processes troff output to render Japanese glyphs as embedded PostScript imagemasks.

Key behavior:
- Parses troff device-independent output commands.
- Tracks horizontal/vertical position and current font.
- Detects the Japanese font slot from `x f` device-control commands.
- For characters in that font, renders the glyph from a Plan 9 bitmap font into a GREY1 image and emits PostScript bitmap commands.
- Passes other troff commands through.

Important details:
- Uses `/lib/font/bit/pelm/unicode.9x24.font`.
- Requires `initdraw`, so it depends on draw/display/font facilities.
- Handles motion, page, font, draw, comment, and device-control commands.

Filesystem relevance:
- Indirect document-output filter; uses font files but no filesystem implementation logic.
