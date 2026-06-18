# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/lib.mak

`lib.mak` is the platform-independent Ghostscript graphics-library makefile. It expects the including top-level makefile to define `GLSRCDIR`, `GLGENDIR`, and `GLOBJDIR`, then derives compiler, include, source, generated, and object path macros.

The first half establishes header dependency macros in bottom-to-top order so older `make` implementations do not mis-expand dependencies. It covers generic headers, platform interfaces, generated configuration headers, C library wrapper headers, Ghostscript memory/GC structures, stream headers, graphics-state headers, device internals, font internals, filters, image processing, color spaces, path machinery, command-list rendering, and optional third-party integrations.

The bulk of the file defines object build rules and `.dev` feature modules for the graphics library: memory managers, bitmap utilities, synchronization, platform misc code, MD5, path/fill/stroke/image/color/font logic, memory devices, bbox/vector/page devices, stream and filter modules, command-list storage, Type 1/Type 2/Type 42/CID font support, pattern color, CIE/ICC/separation color, Display PostScript, transparency, shading, RasterOp, async page rendering, UFST bridge stubs, and platform `gp_*` implementations.

The file also builds pseudo modules such as `libs.dev`, `libx.dev`, `libd.dev`, and `libcore.dev`, using `SETMOD`, `ADDMOD`, `ADDCOMP`, and related generated-device commands. Integration is broad: top-level platform makefiles include this file after defining compiler, path, and feature/device variables.

Filesystem-adjacent pieces include `sfile.dev` for file streams, `clfile.dev` for file-backed band lists, `%rom%` and `%disk%` IODevice support via `gsiorom` and `gsiodisk`, Unix/DOS file-system platform sources, and pipe IODevice support. Risks are makefile fragility, very large manually maintained dependency lists, historical platform conditionals, and several comments noting misplaced modules or optional features that are not part of the base configuration.
