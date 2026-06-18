# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/os2.mak

OS/2 and MS-DOS GCC/EMX or IBM C++ Ghostscript makefile. It sets directory layout, install paths, compiler mode, DLL/executable selection, X11 option, third-party library locations, large color index configuration, processor/FPU flags, assembler use, selected devices, and language features.

The makefile includes the generic Ghostscript make fragments plus `pcwin.mak`, then defines OS/2 platform modules (`gp_os2`, `gp_stdia`), an OS/2 printer IO device feature, auxiliary build programs, generated configuration headers, main `gsos2`/`gsdll2` targets, resources/icons, Presentation Manager helper driver, and ZIP packaging rules.

Dependencies include EMX GCC or IBM C++, OS/2 `LINK386`, `rc`, `emxbind`, bundled JPEG/libpng/zlib/jbig2/icclib, Windows/OS2 device fragments, and platform sources such as `gp_os2.c`, `gp_os2pr.c`, `gdevpm.c`, `gdevos2p.c`, and `gspmdrv.c`.

Filesystem relevance is indirect. The file configures userland Ghostscript builds and printer/file IO choices, but it is not an OS filesystem component.
