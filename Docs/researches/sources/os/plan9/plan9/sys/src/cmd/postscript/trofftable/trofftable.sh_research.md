# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/trofftable/trofftable.sh

Purpose: Generates a PostScript program that builds troff width tables or device descriptions by querying a printer/interpreter.

Key behavior:
- Parses options for copy files, font directory, host font directory, prologue, shell library, device, comments offset, octal escapes, slowdown, and template.
- Sources a shell library from either explicit `-S` or `FONTDIR/dev<DEVICE>/shell.lib`.
- Uses `BuiltinTables` and `awk` to derive the command that builds the requested table.
- Emits PostScript structuring comments and includes configured prologue/data files.
- Supports host-side font file inclusion when available.

Dependencies and integration:
- Built by `trofftable.mk`.
- Requires shell library functions such as `BuiltinTables`.
- Uses `trofftable.ps` and `dpost.ps` style prologues.

Risks and notes:
- Relies on printer serial-port output through PostScript `print`.
- Shell quoting is old-style and not hardened.
- Requires either a device or explicit shell library.
