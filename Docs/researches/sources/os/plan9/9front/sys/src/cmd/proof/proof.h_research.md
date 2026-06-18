# File Research: sources/os/plan9/9front/sys/src/cmd/proof/proof.h

Shared header for the `proof` previewer. It defines page/font/view constants, default magnification, shared renderer state, cursor declarations, font/screen/input function prototypes, and debug macro.

Integration points:
- Included by `font.c`, `htroff.c`, `main.c`, and `screen.c`.
- Declares the custom input API implemented in `main.c`.

Risks:
- Declares `extern int getc(void);`/`ungetc(void);`, intentionally shadowing standard names.
- Fixed constants constrain maximum fonts, sizes, pages, and views.
