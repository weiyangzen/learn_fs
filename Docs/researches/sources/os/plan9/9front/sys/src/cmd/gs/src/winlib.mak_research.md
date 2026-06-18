# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/winlib.mak

Common graphics-library makefile section for 32-bit Windows.

Key points:
- Disables shared third-party libraries for Windows builds, including Jasper.
- Sets default platform `mswin32_`.
- Uses `ccf32.tr` as an auxiliary dependency/response file to avoid command-line length limits.
- Defines Windows command/object/executable syntax and batch wrappers for copy/remove.
- Supports conditional UFST and FreeType bridge flags when `UFST_ROOT` or `FT_ROOT` are set.
- Includes core graphics/device/contrib and bundled-library make fragments.
- Includes `winplat.mak` and `pcwin.mak`.
- Generates blank `gconfig_.h` and standard `gconfigv.h`.
- Defines `mswin32_.dev` from `gp_mswin`, `gp_wgetv`, and `gp_stdia`, including `nosync` and `winplat`.
- Defines separable Windows I/O feature devices: `mshandle.dev`, `msprinter.dev`, and `mspoll.dev`.

Dependencies and interactions:
- Included by Windows platform makefiles before interpreter-specific `winint.mak`.
- Provides platform abstraction modules used by Windows GUI/console/DLL builds.

Research relevance:
- Main Windows platform library layer for Ghostscript device and I/O integration.
