# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdllwin.h

## Role

`gsdllwin.h` adds Microsoft Windows-specific declarations for the old Ghostscript DLL interface.

## API

Declares exported functions:

- `gsdll_copy_dib`
- `gsdll_copy_palette`
- `gsdll_draw`
- `gsdll_get_bitmap_row`

Defines matching function pointer typedefs for runtime dynamic linking.

## Dependencies

Requires Windows types (`HGLOBAL`, `HPALETTE`, `HDC`, `LPRECT`, `LPBITMAPINFOHEADER`, `LPRGBQUAD`, `LPBYTE`) and DLL macros (`GSDLLEXPORT`, `GSDLLAPI`) to be defined by including Windows/old DLL headers first.

## Integration Notes

The API is focused on extracting/drawing bitmap device contents for old Windows GUI front ends.

## Risks

All functions take `unsigned char *device`, so type safety around device identity is weak. The header does not provide ownership rules for returned/copied DIBs or palettes; callers must rely on old DLL API documentation.
