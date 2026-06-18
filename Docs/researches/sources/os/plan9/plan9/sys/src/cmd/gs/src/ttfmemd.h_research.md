# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttfmemd.h

Purpose: declarations for TrueType GC structure descriptors.

Key contents:
- Includes `gsstype.h`.
- Declares external structure descriptors: `st_TFace`, `st_TInstance`, `st_TExecution_Context`, `st_ttfFont`, and `st_ttfInterpreter`.

Dependencies: Ghostscript structure descriptor system.

Integration notes: used by allocation sites in `ttfmain.c`.

Risks: descriptor declarations must match definitions in `ttfmemd.c`.
