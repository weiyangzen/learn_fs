# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dvx-head.mak

## Role
Common platform header makefile fragment for DesqView/X Ghostscript builds.

## Contents
- Sets `PLATFORM=dvx_`.
- Defines command/object/executable suffixes and command-line syntax macros for a DOS/DJGPP-like make environment.
- Defines path separators, shell command variables, copy/remove commands, and genconf arguments.
- Maps internal compiler macros (`CC_D`, `CC_INT`) to `$(CC_)`.
- Clears `PCFBASM` to avoid warnings from PC-specific build pieces that are irrelevant to DV/X.

## Important Interfaces
- Variables consumed by Ghostscript's generic build rules: `CMD`, `OBJ`, `XE`, `D`, `CP_`, `RM_`, `CONFILES`, `CONFLDTR`, `CC_D`, `CC_INT`.

## Dependencies And Coupling
- Included after compiler-specific settings and before generic Ghostscript makefiles.
- Intended to pair with `dvx-tail.mak`.

## Risks And Notes
- Assumes make programs with quirks around trailing spaces and `==`; `NULL` is used to work around this.
- Historical platform support fragment.

## Filesystem Relevance
Only via build path and command variables.
