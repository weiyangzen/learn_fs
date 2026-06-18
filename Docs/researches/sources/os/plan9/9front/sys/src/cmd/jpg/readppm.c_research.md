# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/readppm.c

Netpbm reader for PBM/PGM/PPM variants. `readpixmap` wraps a `Biobuf`, recognizes `P` magic, and delegates to `readppm`.

The `Pix` table covers P1/P4 bitmap, P2/P5 greymap, and P3/P6 pixmap forms. Text forms skip `#` comments and parse decimal fields; raw bitmap uses bit-level reads. Pixel samples are scaled to 0-255 and stored as `CY` or planar `CRGB`.

The file maintains static bit-buffer state for PBM raw reads and flushes it per row. On failures it frees allocated channels and reports a generic format/read/memory error through `errstr`.
