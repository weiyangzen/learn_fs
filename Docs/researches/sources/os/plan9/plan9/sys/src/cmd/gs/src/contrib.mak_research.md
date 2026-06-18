# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/contrib.mak

This makefile defines Ghostscript contributed device drivers and their object/build rules.

Core responsibilities:
- Catalogs user-contributed displays, printers, fax devices, and raster formats, including maintainer/contact comments.
- Defines `.dev` targets using Ghostscript build helpers such as `SETDEV`, `SETPDEV`, and `ADDMOD`.
- Defines object dependencies and compile commands for each contributed driver.

Major categories:
- Displays: Hercules, Private Eye, AT&T 3b1, Sony framebuffer, SunView.
- Printer families: Apple/ImageWriter, Canon BubbleJet, HP DeskJet/PaintJet/DesignJet/Color LaserJet, Epson/ESC-P, Brother, Canon LBP/LIPS, NEC/LQ, Lexmark, Okidata, Ricoh, SPARCprinter, Tektronix, and others.
- Fax devices: CAPI fax and DigiFAX low/high resolution.
- Raster/file output formats: CIF, Inferno bitmaps, MGR, SGI RGB, and Sun raster variants.

Plan 9 relevance:
- The `inferno.dev` target builds `gdevifno.c`, credited to Russ Cox, for Inferno bitmap output. This is adjacent to Plan 9/Inferno history but still a Ghostscript output-device rule, not OS filesystem code.

Build behavior:
- Some `.dev` targets reuse one object for several device names.
- Some devices add libraries or include other device modules.
- Dependencies rely on Ghostscript generic printer/device headers and shared support modules such as HPPCL and fax stream support.

Filesystem relevance is limited to build artifacts and output-device formats; runtime file I/O is implemented elsewhere in Ghostscript.
