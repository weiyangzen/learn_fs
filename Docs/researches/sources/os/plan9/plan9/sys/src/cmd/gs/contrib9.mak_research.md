# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/contrib9.mak

This Ghostscript make fragment reintroduces contributed drivers not found in the current upstream distribution. It defines build rules for the Plan 9 bitmap device (`plan9.dev`) and several HP DeskJet-derived color printer devices (`cdj850`, `cdj670`, `cdj890`, `cdj1600`).

The rules set device objects with Ghostscript make macros and compile `gdevplan9.c` and `gdevcd8.c` with the configured Ghostscript compiler variables.

It is Plan 9 port build glue for bundled Ghostscript.
