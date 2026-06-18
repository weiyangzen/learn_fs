# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/macosx.mak

`macosx.mak` is the Darwin/gcc Ghostscript configuration makefile. It sets build directories, framework installation paths, runtime resource paths, compiler/linker flags, third-party library choices, feature devices, output devices, and Ghostscript platform policy.

It targets a framework-style installation under `/Library/Frameworks/Ghostscript.framework`. Runtime search paths cover bundled library/resources plus `/Library/Fonts` and `/System/Library/Fonts`. It enables `HAVE_MKSTEMP`, uses `cc`, chooses bundled JPEG/PNG/JBIG2/ICC with shared zlib, and defaults to `nosync`.

The default devices emphasize file conversion on macOS: PNG devices, selected PNM/PBM/PGM devices, JPEG devices, PDF/PS writers, PXL, and bbox. X11/display support is disabled by default. Band lists default to file storage, file I/O uses `stdio`, and stdio uses callouts.

The file includes the main Unix/Ghostscript make fragments plus `macos-fw.mak` for shared library and framework targets. Risks are historical Darwin assumptions, framework-oriented shared-object install naming, and no pthread synchronization unless the platform configuration is changed.
