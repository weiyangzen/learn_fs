# File Research: sources/os/plan9/plan9/sys/src/cmd/page/gfx.c

Implements graphics-file support for `page`. It builds a `Document` whose pages are individual image files or one stdin image, and whose `drawpage` converts the selected graphic into a Plan 9 image.

`genaddpage` classifies formats by magic bytes and filename suffix: Plan 9 bitmaps, Inferno compressed images, GIF, TIFF, JPEG, PNG, PPM, BMP, YUV, fax/CCITT, and fallback `cvt2pic`. Conversion commands are stored in `cvt[]`, with true-color variants for some formats.

`convert` either reads native Plan 9 images directly or spawns `/bin/rc -c <converter>`, optionally feeding a stdin buffer through a pipe, then `readimage`s converter output. Converter wait statuses are reported except for known special cases.

The document supports dynamic `addpage`/`rmpage`, enabling plumbed image additions and interactive discard from the viewer.
