# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postbgi/postbgi.h

BGI opcode and helper definitions for `postbgi`.

Key responsibilities:
- Defines BGI command opcodes and data masks.
- Defines character size, vector modes, visibility modes, fill/outline modes, line-style constants, color component constants, and helper macros.
- Defines `Disp` for subroutine displacement tracking.
- Defines `Fontmap` and default font-name aliases.
- Declares `get_font()`.

Important behavior:
- `MAG()` decodes sign-magnitude BGI integer bytes.
- `LINESPACE()` derives text line spacing from BGI character grid size.
- `STYLES` maps BGI line styles to PostScript dash arrays.
