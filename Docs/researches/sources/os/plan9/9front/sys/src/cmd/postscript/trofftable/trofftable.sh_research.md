# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/trofftable/trofftable.sh

Shell script that emits a PostScript program for building troff width tables or typesetter description files on a printer. It sources a device/library shell file, finds the built-in table command for a template/font, then concatenates prologues, optional host font/copy files, setup parameters, the generated command, and trailer.

Key behavior:
- Supports options for copy files, font directory, host font directory, prologue, shell library, device, start comments, octal escapes, slowdown, and template.
- Requires either `-T device` or `-S library`.
- Sources `${LIBRARY:-${FONTDIR}/dev${DEVICE}/shell.lib}` and calls `BuiltinTables`.

Integration points:
- Uses `trofftable.ps` and `dpost.ps`.
- Intended to communicate generated table output over a printer’s serial channel.

Risks:
- Sourcing device/library scripts executes local shell code.
- Command construction depends on shell library output format and `awk`.
