# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/buildtables/buildtables.sh

Shell helper for building PostScript troff font width tables.

Key responsibilities:
- Parses options for font directory, device, shell library, serial line, baud rate, and trofftable options.
- Loads a shell library and expands default table list with `AllTables` when no table names are supplied.
- Runs `trofftable` to generate PostScript table programs.
- Optionally sends them to a printer line via `postio` and saves returned tables.

Important behavior:
- Requires either `-T device` or `-S library`.
- Builds library path as `$FONTDIR/dev$DEVICE/shell.lib` by default.
- Each table argument is split into short and long names by `awk`.

Notable risks:
- Uses legacy shell syntax and unquoted expansions in several places.
