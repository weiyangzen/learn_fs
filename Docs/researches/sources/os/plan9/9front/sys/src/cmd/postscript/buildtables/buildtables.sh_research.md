# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/buildtables/buildtables.sh

`buildtables.sh` builds troff font width tables or typesetter descriptions on a PostScript printer. It parses device, font dir, shell library, line, baud, and trofftable options; sources a shell library when no explicit table arguments are provided; runs `trofftable`; and optionally sends generated PostScript to a printer via `postio`.
