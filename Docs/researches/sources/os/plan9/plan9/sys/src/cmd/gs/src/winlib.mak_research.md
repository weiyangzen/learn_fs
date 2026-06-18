# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/winlib.mak

Common 32-bit Windows library makefile section.

Key points:
- Forces bundled/non-shared third-party libraries for JPEG, libpng, zlib, JBIG2, and Jasper.
- Defaults `PLATFORM=mswin32_`.
- Defines `AK=$(GLGENDIR)\ccf32.tr` to avoid command-line length limits.
- Defines Windows command syntax and batch-file copy/remove helpers.
- Sets optional bridge flags for UFST and FreeType if corresponding roots are set.
- Includes core library/device/contrib make fragments and Windows platform fragments.
- Generates blank `gconfig_.h` and `gconfigv.h`.
- Builds `mswin32_.dev` from `gp_mswin`, `gp_wgetv`, `gp_stdia`, and includes `nosync` plus `winplat`.
- Defines separable Windows I/O features: `mshandle.dev`, `msprinter.dev`, and `mspoll.dev`.

Dependencies and interactions:
- Used by Windows compiler-specific makefiles before `winint.mak`.
- Coordinates graphics-library platform objects and Windows-specific IO devices.

Research relevance:
- Defines the Windows platform module set and Windows-specific Ghostscript IO devices.
