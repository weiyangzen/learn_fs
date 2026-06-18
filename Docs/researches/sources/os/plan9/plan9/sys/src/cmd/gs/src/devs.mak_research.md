# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/devs.mak

## Purpose

`devs.mak` is Ghostscript's device-driver makefile catalog. It does not implement runtime logic; it declares device names, object dependencies, build recipes, module composition, and library/includes needed to compile display, printer, high-level writer, and raster-output devices.

## Main Structure

- Defines common dependency bundles such as `GDEVH`, `GDEV`, and `PDEVH`.
- Documents the device catalog and conventional `DEVICE_DEVS*` grouping used by higher-level makefiles.
- Provides rules for display devices: DOS EGA/VGA/SVGA, DLL display, Linux `vgalib`, and X11 plus alternate X11 testing devices.
- Provides printer and writer devices: HP PCL/LaserJet, IJS, `rinkj`, PostScript/EPS/PDF writers, and PCL XL writers.
- Provides raster file devices: raw bits, BMP, CGM, DeviceN, XCF, PSD, JPEG, MIFF, PCX, PBM/PGM/PPM/PAM, Plan 9 bitmap, PNG, PostScript image, fax, and TIFF variants.

## Plan 9 / Filesystem Relevance

The file lives in the Plan 9 source tree because this tree vendors Ghostscript. The direct Plan 9-related entry is `plan9bm.dev`, listed as the Plan 9 bitmap format device. It is built from the shared PNM/PBM driver object group `pxm_`, meaning Plan 9 bitmap output is handled by the common portable-map raster driver family rather than a separate large device module.

## Important Build Relationships

- `display.dev` packages `gdevdsp`, color mapping, DeviceN/equivalent color, and CRD support for platforms using Ghostscript's display callback API.
- `x11_.dev` composes X11 core objects and links external X libraries via `XLIBDIRS`/`XLIBS`.
- `pdfwrite.dev` is a large module composed from many `gdevpdf*` objects, compression/filter modules, `psdf.dev`, and `pdtext.dev`.
- `pdtext.dev` / `pdxtext.dev` isolate PDF text extraction/embedding support as a separate logical module used by `pdfwrite`.
- `png*.dev` depends on generated `libpng.dev` and includes the libpng module.
- TIFF fax variants are layered through `fax.dev`, `tfax.dev`, and `tiffs.dev`.

## Dependencies / Interfaces

This makefile relies on Ghostscript make variables supplied elsewhere, including `GLSRC`, `GLOBJ`, `DD`, `GLD`, `OBJ`, `GLCC`, `SETDEV`, `SETPDEV`, `SETMOD`, `ADDMOD`, `ECHOGS_XE`, `XINCLUDE`, `XLIBS`, `PNGGENDIR`, and many header-path variables.

## Research Notes

- This file is mostly build metadata, but it is central to which Ghostscript devices are available in a Plan 9 build.
- Device modules are often hierarchical: small `.dev` targets include common `.dev` modules rather than duplicating object lists.
- Any attempt to add/remove Ghostscript output devices in this tree must update this catalog consistently with the surrounding makefile macros.
