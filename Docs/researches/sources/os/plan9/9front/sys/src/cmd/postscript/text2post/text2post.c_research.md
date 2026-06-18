# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/text2post/text2post.c

Plan 9 `bio`-based text-to-PostScript translator, adapted from `postprint` but supporting encoded runes where high byte selects a Lucida/Courier font slot. It emits DSC/prologue/setup, translates input into PostScript `show`, spacing, and tab operations, tracks used fonts, supports page selection, and writes trailer font/page summaries.

Key behavior:
- Large `charcode[256]` table escapes all byte values for PostScript strings.
- `fontname[]` maps font byte slots to LucidaSansUnicode blocks and Courier fallback.
- `prologues` emits `postprint` prologue, tab/space helpers, encoding setup, forms setup, and unknown-character prologue.
- `txt2post` reads runes, separates low-byte character and high-byte font id, handles spaces/tabs/backspaces/newlines/formfeeds, changes fonts, and uses `pw` for unknown font slots.
- `pagelist` builds a bitmap of pages to print.

Integration points:
- Uses Plan 9 `<u.h>`, `<libc.h>`, `<bio.h>`, and shared `comments.h`/`path.h`.
- Depends on `POSTPRINT`, `ROUNDPAGE`, `FORMFILE`, `ENCODINGDIR`, and `/sys/lib/postscript/prologues/pjw.char.ps`.

Risks:
- `pagelist` grows `pplist` with `realloc` but does not zero newly allocated bytes before OR-ing page bits.
- `cat` opens the file twice and assigns globals unnecessarily; one handle is not closed.
- String/font memory allocated from options is not freed, acceptable for short process lifetime.
