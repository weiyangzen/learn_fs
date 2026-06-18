# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/devs.mak

This is Ghostscript's central makefile fragment for Aladdin/Artifex-maintained device drivers. It catalogs display, printer, high-level writer, raster image, fax, TIFF, PNG, JPEG, and utility devices, then defines the object/module rules used by platform makefiles to include those devices in a build.

Key responsibilities:
- Defines common device dependencies through `GDEVH`, `GDEV`, and printer dependency `PDEVH`.
- Documents the intended `DEVICE_DEVS` through `DEVICE_DEVS20` grouping convention, partly constrained by MS-DOS command-line length limits.
- Lists supported driver names and their user-facing purpose, including MS-DOS EGA/VGA/SVGA, X11, label printers, HP PCL devices, fax/TIFF devices, PNG/JPEG/BMP/PCX/PBM/PNM file devices, and high-level PDF/PS/PCL XL writers.
- Builds shared support objects such as `gdevpccm`, `gdevpcfb`, `gdevpsu`, `gdevdcrd`, `gdevdevn`, `gsequivc`, and format-specific helper objects.
- Uses Ghostscript build tools/macros such as `$(SETDEV)`, `$(SETDEV2)`, `$(SETPDEV)`, `$(SETPDEV2)`, `$(SETMOD)`, and `$(ADDMOD)` to assemble `.dev` modules.
- Pulls in external or separately built libraries for some devices, such as X11 libraries, vgalib, IJS, libpng, zlib filters, JPEG/DCT filters, LZW/RLE/CCITT filters, and ICC-enabled code.

Major device groups:
- Display devices: `ega`, `vga`, `svga16`, chipset-specific SVGA devices, `s3vga`, `display`, `lvga256`, `vgalib`, and X11 variants including CMYK/gray/mono/testing modes.
- Printer devices: Practical Automation `atx*`, HP DeskJet/LaserJet/PCL devices, `lj5mono`, `lj5gray`, and the IJS and Rinkj client paths.
- High-level output: shared `psdf`, `epswrite`, `pswrite`, `pdfwrite`, `ps2write`, `pdtext`/`pdxtext`, and `pxlmono`/`pxlcolor`.
- Raster/file outputs: `bit*`, `bmp*`, `cgm*`, `spotcmyk`, `devicen`, `xcf`, `psd*`, `perm`, `jpeg*`, `miff24`, `pcx*`, `pbm`/`pgm`/`ppm`/`pnm`/`pam`, `plan9bm`, `png*`, `pnga`, `psmono`/`psgray`/`psrgb`, fax, and TIFF variants.

Notable implementation details:
- `plan9bm.dev` is present as a Ghostscript raster output device for Plan 9 bitmap format, but this file itself is still generic Ghostscript build metadata.
- PNG devices depend on generated `libpng.dev` and include libpng via `png_i_`.
- `pdfwrite.dev` also creates `ps2write` and includes a large set of filter, color, text, and `psdf` modules.
- The PDF text subsystem is split into its own `pdtext`/`pdxtext` module due to size and complexity.
- Some devices are explicitly marked as contributed or hardware-dependent, and the comments direct users away from Aladdin support for those cases.
- Several historical platform assumptions are embedded, including MS-DOS, SCO/Xenix direct framebuffer notes, vgalib, and legacy printer guidance.

Filesystem relevance:
- This is build orchestration, not filesystem implementation.
- It defines output devices that may write files, including `plan9bm`, PNG/JPEG/TIFF/BMP/PNM/PDF/PS outputs, but file I/O behavior lives in the corresponding C device implementations and Ghostscript I/O layers.
- Its relevance to subset A is source-tree inventory coverage under the 9front Ghostscript tree, not OS VFS or storage behavior.

Research classification: Ghostscript device build catalog and module recipe file, broad build-surface metadata for display/printer/file-format drivers.
