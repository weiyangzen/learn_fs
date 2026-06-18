# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/lib.mak

## Purpose
Platform-independent Ghostscript graphics-library make fragment. It defines generated/source/object directory aliases, compiler command macros, header dependency macros, object compilation rules, and `.dev` module assembly rules for the core graphics library and many optional Ghostscript facilities.

## Main Structure
- Establishes `GLSRC`, `GLGEN`, `GLOBJ`, `GLCC`, specialized compiler wrappers for JPEG/zlib/ICC/JBIG2, and `LIB_MAK`.
- Defines dependency aliases for generic headers, platform interfaces, generated configuration headers, C library wrapper headers, memory manager headers, graphics headers, stream/filter headers, color/font/image/device headers, and auxiliary generator dependencies.
- Provides object rules for memory management, bitmap operations, synchronization, platform glue, MD5, visual debugging, graphics state/path/color/image/font/device code, filters, clists, page/vector devices, Type 1/TrueType/CID/pattern/shading/transparency support, ROM/disk/Mac resource IODevices, UFST bridge hooks, and platform-specific shared modules.
- Assembles feature/device modules with `SETMOD`, `ADDMOD`, `SETDEV`, `SETDEV2`, `ADDCOMP`, and `-replace`/`-include` relationships.

## Important Build Products
- Core library features: `libs.dev`, `libx.dev`, `libd.dev`, `libcore.dev`.
- Stream/filter modules: `sfile.dev`, `cfe.dev`, `cfd.dev`, `sdcte.dev`, `sdctd.dev`, `lzwe.dev`, `lzwd.dev`, `smd5.dev`, `sarc4.dev`, `saes.dev`, `sjbig2.dev`, `sjpx.dev`, `pdiff.dev`, `pngp.dev`, `rle.dev`, `rld.dev`, `szlibe.dev`, `szlibd.dev`.
- Device/library features: `page.dev`, `clist.dev`, `vector.dev`, `iscale.dev`, `roplib.dev`, `async.dev`, `ttflib.dev`, `cidlib.dev`, `cmaplib.dev`, `patlib.dev`, `psf1lib.dev`, `psf2lib.dev`, `cmyklib.dev`, `psl2lib.dev`, `funclib.dev`, `cielib.dev`, `sicclib.dev`, `psl3lib.dev`, `translib.dev`, `shadelib.dev`, `romfs.dev`, `macres.dev`.

## Integration Notes
- Consumed by platform makefiles such as Unix, Mac, and Windows builds after they define directory, compiler, and module-building macros.
- Depends on other partial makefiles for generated configuration/device metadata and third-party libraries.
- `md5.c` is built through a generated wrapper header/copy path so `memory_.h` is included before the original MD5 header.

## Risks and Edge Cases
- Very macro-heavy; missing platform definitions break many rules indirectly.
- Some dependencies reference names that are not defined locally or look inconsistent in this file, including `memory_h`, `stdint_`, `vtrace_h`, `gsdebug_h`, and `gsfixed_h`; these may be supplied by other make fragments or may be old makefile defects.
- `.dev` module ordering matters because later features replace or include earlier pseudo-features.
- Clean separation between base, optional, and testing-only modules is encoded only by variable membership and `.dev` inclusion, not by a central manifest.
