# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/int.mak

Platform-independent Ghostscript makefile for PostScript, PDF, Display PostScript, and related interpreter features.

Key behavior:
- Defines interpreter source/object directory macros and compiler command wrappers.
- Declares common interpreter headers, nested header dependencies, and object build rules.
- Builds core support modules such as allocator, GC, name table, save/restore, dictionaries, stacks, parameters, scanner, plugin manager, and interpreter.
- Defines `psbase.dev`, the base PostScript interpreter module, including core operators, IODevices, support modules, and stream filters.
- Defines feature `.dev` modules for Level 1, Level 2, Level 3, PDF, DSC parsing, color, patterns, CIE, separations, filters, binary tokens, user parameters, Display PostScript, CID/CMap, Type 1/2/32/42 fonts, compiled fonts, stochastic halftones, transparency, ICC, disk IODevices, and Font API bridges.
- Uses module composition commands such as `SETMOD` and `ADDMOD` to add objects, operators, PostScript resources, emulators, IODevices, plugins, replacement modules, function types, and links.
- Provides stub modules such as `nobtoken`, `nousparm`, `fapiu`, and `fapif` that can be replaced by richer features.
- Defines final main-program object dependencies for `gs.c`, `iapi.c`, `icontext.c`, `idisp.c`, `imainarg.c`, `imain.c`, `interp.c`, and `ireclaim.c`.

Notable dependencies:
- Ties interpreter C files in `PSSRCDIR` to graphics-library modules under `GLSRC`, `GLD`, and `GLOBJ`.
- References optional external libraries/bridges including JBIG2, JPX/Jasper, UFST, and FreeType.

Research notes:
- This file is the central interpreter feature graph; changing it can affect which operators, PostScript initialization files, and replacement stubs are present in a build.
- It explicitly separates small fallback implementations from feature replacements, for example `nobtoken` versus `btoken`, and `nousparm` versus `usparam`.
- There is a likely typo in the `zht2.$(OBJ)` dependency list: it references `$(iname)` rather than the established `$(iname_h)`.
