# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/contrib.mak

This makefile defines contributed Ghostscript device drivers and their object/build rules.

Key responsibilities:
- Catalogs user-contributed display, printer, fax, and raster file devices with maintainer/contact comments.
- Defines `.dev` targets by grouping object files and adding them with `$(SETDEV)`, `$(SETPDEV)`, and `$(ADDMOD)`.
- Provides object compile rules for many contributed driver source files.
- Organizes devices by category:
  - MS-DOS displays: Hercules, Private Eye
  - Unix/VMS displays: AT&T 3b1, Sony framebuffer, SunView
  - Printer families: Apple, Canon, CalComp, HP, CoStar, Mitsubishi, Epson, Omni, Brother, Imagen, IBM, Canon LBP/LIPS, Lexmark, Okidata, Ricoh, Sony, SPARCprinter, StarJet, Tektronix
  - Fax: CAPI fax and DigiFAX
  - Raster/file formats: CIF, Inferno bitmaps, MGR, SGI RGB, Sun raster variants

Important Plan 9-adjacent note:
- The `inferno` bitmap device is explicitly credited to Russ Cox at `plan9.bell-labs.com`, but it is still a Ghostscript raster output device rule, not a Plan 9 filesystem component.

Important build relationships:
- Many printer devices depend on common page device support `$(DD)page.dev`.
- HP/PCL-style devices often depend on `$(HPPCL)` and `gdevpcl_h`.
- Fax devices include fax module dependencies such as `$(DD)fax.dev` or `$(DD)tfax.dev`.
- Shared object groups let multiple devices reuse the same implementation object, for example Epson and IBM Proprinter variants.

Notable implementation details and risks:
- The file is contributor-maintained, and comments direct bugs to device authors rather than core Ghostscript channels.
- It is broad build metadata, not device implementation itself.
- It maps a large hardware/output surface, useful for understanding why Ghostscript builds pull in many legacy drivers.
- No filesystem, VFS, block, or storage substrate logic is present.

Research classification: Ghostscript contributed-device build catalog.
