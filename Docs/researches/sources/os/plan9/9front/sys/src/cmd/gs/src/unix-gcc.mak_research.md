# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/unix-gcc.mak

Top-level Unix/gcc/X11 Ghostscript makefile.

Key points:
- Configures build directories, install directories, runtime search path, init file, feature/device list, third-party source directories, archive tools, compiler/linker flags, X11 include/lib paths, FPU setting, and synchronization module.
- Defaults to `gcc`, `-O2`, `-Wall`, strict prototype warnings, `-fno-builtin`, `-fno-common`, and `-DHAVE_MKSTEMP`.
- Defaults to `SYNC=nosync` and `STDLIBS=-lm`; comments explain how to enable POSIX sync with pthreads.
- Enables language features including PostScript Level 3, PDF, DPS, TrueType font support, EPSF, pipe device, and FAPI.
- Selects a broad set of X11, printer, raster image, TIFF, PNG, JPEG, PDF/PS/PXL writer, bbox, DeviceN, and spot-color devices.
- Adds `GX_COLOR_INDEX_TYPE='unsigned long long'`.
- Includes the full chain of Ghostscript make fragments: Unix head, graphics library, interpreter, compiled fonts, image libraries, ICC/IJS, devices, contrib, Unix auxiliary/link/DLL/end/install fragments.
- Generates `$(AK)` by detecting old gcc 2.7 optimizer bugs and writing either `-Dconst=` or warning flags.

Dependencies and interactions:
- Main Unix build driver for this Ghostscript tree.
- Pulls together graphics library, PostScript interpreter, bundled libraries, device modules, and install/shared-library fragments.

Research relevance:
- Defines the canonical GCC Unix build configuration and device surface for this vendored Ghostscript snapshot.
