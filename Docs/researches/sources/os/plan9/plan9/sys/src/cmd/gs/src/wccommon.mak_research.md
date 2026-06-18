# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/wccommon.mak

Common Watcom C/C++ makefile section for MS-DOS and Windows.

Key points:
- Used by Watcom DOS/Windows makefiles and documents required input variables.
- Enables `.NOCHECK` and adds extensions to satisfy Watcom make.
- Forces built-in third-party libraries: `SHARE_JPEG=0`, `SHARE_LIBPNG=0`, `SHARE_ZLIB=0`, `SHARE_JBIG2=0`.
- Defines DOS/Watcom command syntax, path separator, object/executable extensions, batch-file copy/remove commands, and `genconf` argument forms.
- Selects Watcom compiler/linker/resource tools based on `WCVERSION`, including 9.5, 10.0, 10.5, 11.0, and 10.695 hosted tools.
- Sets include directories, binder, CPU/FPU-derived flags, assembly/object rules, and default target.
- Computes debug/privacy flags and final compiler command macros: `CC`, `CCAUX`, `CC_`, `CC_D`, `CC_INT`, and `CC_NO_WARN`.

Dependencies and interactions:
- Included before `wctail.mak` and platform-specific make logic.
- Centralizes Watcom command-line spelling and tool selection.

Research relevance:
- Encapsulates the Watcom build system portability layer.
