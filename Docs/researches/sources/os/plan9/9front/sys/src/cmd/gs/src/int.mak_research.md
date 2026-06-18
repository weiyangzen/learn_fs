# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/int.mak

Platform-independent Ghostscript makefile for the PostScript and PDF interpreter layers. It defines source/include variables, module dependencies, object build rules, feature `.dev` modules, interpreter levels, PDF support, font support, filter support, plugin bridges, and main-program build targets.

Key contents:
- Defines interpreter source/object prefixes such as `PSSRC`, `PSLIB`, `PSGEN`, `PSOBJ`, `PSCC`, and `PSJBIG2CC`.
- Declares core interpreter support headers and nested include relationships, including the headers in this group: `inameidx.h`, `inamestr.h`, `inamedef.h`, `ipacked.h`, `iref.h`, `interp.h`, `iparam.h`, `iosdata.h`, `iostack.h`, `iparray.h`, `ipcolor.h`, and `iplugin.h`.
- Builds core support modules such as `ialloc`, `igc`, `igcref`, `igcstr`, `ilocate`, `iname`, and `isave` into `isupport.dev`.
- Builds interpreter support objects including `iparam`, `iplugin`, and the main `interp` object.
- Defines `psbase.dev` from interpreter runtime objects, non-graphics operators, graphics operators, scanner/token support, streams, basic IODevices, and default replacements `nobtoken` and `nousparm`.
- Defines feature modules for Level 1, Level 2, Level 3, Display PostScript, PDF, filters, fonts, CMaps, CIDFonts, CIE color, patterns, separation, transparency, ICC, `%disk` IODevices, and FAPI bridges.
- Provides explicit fallback and replacement modules:
  - `nobtoken.dev` from `inobtokn.c`, replaced by `btoken.dev`.
  - `nousparm.dev` from `inouparm.c`, replaced by `usparam.dev`.
- Defines build rules for auxiliary/generated artifacts such as compiled init code, compiled fonts, stochastic halftones, and generated configuration tables.
- Defines main program object rules for `gs.c`, `iapi.c`, `icontext.c`, `idisp.c`, `imainarg.c`, `imain.c`, `interp.c`, and `ireclaim.c`.

Notable dependencies:
- Graphics-library make variables and generated module tooling: `SETMOD`, `ADDMOD`, `GENCONF_XE`, `GENINIT_XE`, `GENHT_XE`.
- Core Ghostscript graphics library modules under `GLD`, `GLOBJ`, and `GLSRC`.
- Optional external libraries or bridges for zlib, JPEG, JBIG2, JPX/Jasper, UFST, and FreeType depending on enabled features.

Research notes:
- This file is the build graph for much of the language interpreter, not ordinary C source.
- It shows that several files in this group are low-level defaults or infrastructure rather than standalone features.
- The PDF build intentionally pulls in nearly all LanguageLevel 3 support rather than finely factoring only the needed operators.
- Some old compatibility comments remain, including alias targets `level1.dev`/`level2.dev`, DOS shell line-length constraints for font lists, and linker-order constraints around core libraries.
- There is a likely typo in the AES filter section: `faes4_=$(PSOBJ)zfaes.$(OBJ)` is defined, but `faes.dev` depends on and adds `$(faes_)`, which is not defined in the visible file.
