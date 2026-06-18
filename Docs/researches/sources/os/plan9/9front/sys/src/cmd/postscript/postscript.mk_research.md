# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postscript.mk

Top-level makefile for the DWB/PostScript package. It documents configuration variables, exports install/build settings, and recursively builds, installs, cleans, clobbers, or rewrites subdirectories named in `TARGETS`.

Key behavior:
- Default targets include common libraries, translators, prologues, font tools, printer I/O tools, and `trofftable`.
- `install` and `changes` export path/version variables to sub-makes.
- Per-target rule clears inherited object/header/link variables and runs `$@/$@.mk` when present.
- `changes` is intended to synchronize low-level makefiles, manpages, and source definitions after config edits.

Integration points:
- Coordinates all sibling postscript package directories.
- Shared settings include `FONTDIR`, `HOSTDIR`, `POSTBIN`, `POSTLIB`, `TMACDIR`, `DKHOST`, `DKSTREAMS`, and `ROUNDPAGE`.

Risks:
- Recursive make assumes each target directory makefile follows the same naming convention.
- Install defaults target system paths under `/usr`; `ROOT` can redirect but defaults empty.
- Comments mention typo `dpsot`; behavior unaffected.
