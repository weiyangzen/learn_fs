# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpxop.h

This header defines PCL XL operator and data tag byte values in `px_tag_t`. The enum covers the full one-byte tag space, including placeholders for unassigned values, so byte positions remain protocol-stable.

Covered tag families include:
- Session/page/data-source operators such as `pxtBeginSession`, `pxtEndSession`, `pxtBeginPage`, `pxtEndPage`, `pxtOpenDataSource`, and `pxtCloseDataSource`.
- Font and downloaded-character operators such as `pxtBeginFontHeader`, `pxtReadFontHeader`, `pxtBeginChar`, `pxtReadChar`, `pxtEndChar`, `pxtRemoveFont`, and `pxtSetFont`.
- Graphics-state operators such as `pxtPushGS`, `pxtPopGS`, clipping, cursor, color space, halftone, fill mode, line state, ROP, and transparency mode.
- Path and painting operators such as `pxtLinePath`, `pxtBezierPath`, `pxtRectangle`, `pxtText`, and related relative/list forms.
- Raster/image operators such as `pxtBeginImage`, `pxtReadImage`, `pxtEndImage`, raster pattern operators, and scan operators.
- Data type tags for unsigned/signed integers, real values, arrays, xy pairs, boxes, attribute tags, and data-length markers.

The driver writes these values directly as bytes; this header is the low-level opcode table for `gdevpx.c` and `gdevpxut.c`.
