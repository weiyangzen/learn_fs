# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/unixhead.mak

Common Unix makefile header fragment.

Key points:
- Sets `PLATFORM=unix_`.
- Defines command/object/executable syntax variables for Unix builds: `C_`, `D_`, `I_`, `O_`, `OBJ=o`, empty `XE`, `/` path separator, `/bin/sh`, `cat`, `cp`, and `rm -f`.
- Defines `CONFILES` and `CONFLDTR` arguments for `genconf`.
- Defines `CC_D`, `CC_INT`, and empty `BEGINFILES`.
- Clears PC-specific assembly placeholders such as `PCFBASM`.
- Defines `std: STDDIRS default`.

Dependencies and interactions:
- Included after compiler-specific options and before core Ghostscript makefiles.
- Provides variable conventions consumed throughout all Unix make fragments.

Research relevance:
- Establishes the Unix make variable ABI for the rest of the Ghostscript build system.
