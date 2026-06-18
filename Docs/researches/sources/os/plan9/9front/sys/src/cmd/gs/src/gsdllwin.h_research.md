# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdllwin.h

This header extends the old DLL interface for Microsoft Windows display/bitmap operations.

Exported functions:
- `gsdll_copy_dib`
- `gsdll_copy_palette`
- `gsdll_draw`
- `gsdll_get_bitmap_row`

It also declares matching runtime dynamic-linking function pointer typedefs. Types such as `HGLOBAL`, `HPALETTE`, `HDC`, `LPRECT`, `LPBITMAPINFOHEADER`, `LPRGBQUAD`, and `LPBYTE` are Windows API types expected from the Windows build environment.

This is compatibility API surface for GUI clients that need direct bitmap or drawing access.
