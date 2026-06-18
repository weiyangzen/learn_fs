# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmac.h

Header for the legacy Classic MacOS PICT device and xfont integration.

Key contents:
- Includes Classic MacOS headers: `Fonts.h`, `FixMath.h`, `Resources.h`, plus Ghostscript device, xfont, struct, DLL, and utility headers.
- Defines default page/device dimensions and dpi values for the `macos` device.
- Defines `gx_device_macos`, extending Ghostscript device/printer-style state with:
  - Output filename and `FILE *`.
  - PICT handle and current PICT pointer.
  - `outputPage` reset state.
  - `useXFonts`.
  - Last-used font face/size/family and a list of used font family IDs.
- Declares all Mac device procs: open, matrix, sync, output, params, close, fill, strip-tile, mono/color copy, line, alpha, and xfont procs.
- Defines `mac_xfont`, carrying Ghostscript xfont common state plus Mac font name, family, face, size, encoding, and metrics.
- Defines `CheckMem` to grow the PICT handle while preserving `currPicPos`.
- Defines `ResetPage` to reset PICT drawing after page output and clear font caches.
- Defines RGB/HSV helper structs and private helper prototypes.
- Exports `gsdll_get_pict` under `#pragma export`.

Dependencies and notes:
- `gdevmac.c` and `gdevmacxf.c` share this header.
- The header assumes Classic/Carbon Mac type names and resource APIs are available.
