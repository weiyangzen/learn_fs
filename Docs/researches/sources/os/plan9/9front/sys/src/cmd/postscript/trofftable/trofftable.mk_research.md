# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/trofftable/trofftable.mk

Makefile that generates and installs the `trofftable` shell script and its PostScript support/manpage. It substitutes configured `FONTDIR`, `POSTBIN`, and `POSTLIB` into `trofftable.sh`, installs `trofftable`, `trofftable.ps`, and `trofftable.1`, and supports `changes` for propagating config into the makefile/manpage.

Integration points:
- Part of top-level `postscript.mk` target list.
- Installs into the same PostScript bin/lib directory scheme as other tools.

Risks:
- `clean` is empty; generated script remains until `clobber`.
- Install target assumes `MAN1DIR` exists.
