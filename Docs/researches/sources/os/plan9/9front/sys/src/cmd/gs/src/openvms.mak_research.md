# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/openvms.mak

OpenVMS platform makefile for the Ghostscript tree. It configures VAX/Alpha OpenVMS builds, output/source/object directories, runtime search paths, third-party library source locations, compiler/linker commands, selected devices/features, and generated build metadata.

The makefile includes the generic Ghostscript make fragments (`gs.mak`, `lib.mak`, `int.mak`, `jpeg.mak`, `zlib.mak`, `libpng.mak`, `jbig2.mak`, `icclib.mak`, `devs.mak`, `contrib.mak`) and adapts their variables to OpenVMS syntax. It builds helper programs such as `echogs`, `genarch`, `genconf`, `gendev`, `genht`, and `geninit`, creates `openvms.com`/`openvms.opt`, and emits `gconfig_.h`/`gconfigv.h`.

Dependencies are OpenVMS DCL commands, DEC C, OpenVMS linker option files, DECwindows/X11 libraries, bundled JPEG/libpng/zlib/jbig2/icclib sources, and Ghostscript platform files such as `gp_vms.c` and `gp_stdia.c`.

Filesystem relevance is indirect. This is userland build orchestration for a vendored Ghostscript copy in 9front, not Plan 9 filesystem code.
