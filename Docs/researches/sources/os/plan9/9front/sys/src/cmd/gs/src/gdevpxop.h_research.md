# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpxop.h

This header defines PCL XL operator and data tag byte values in `px_tag_t`.

The enum covers the full byte tag space:
- Session/page/data-source tags such as `pxtBeginSession`, `pxtEndSession`, `pxtBeginPage`, `pxtEndPage`, `pxtOpenDataSource`, and `pxtCloseDataSource`.
- Font and character download operators such as `pxtBeginFontHeader`, `pxtReadFontHeader`, `pxtBeginChar`, `pxtReadChar`, and `pxtSetFont`.
- Graphics state operators such as `pxtPushGS`, `pxtPopGS`, clipping, color space, cursor, halftone, fill mode, line state, ROP, and transparency mode.
- Path construction and painting operators such as `pxtLinePath`, `pxtBezierPath`, `pxtRectangle`, `pxtText`, and related relative/list forms.
- Raster/image operators such as `pxtBeginImage`, `pxtReadImage`, `pxtEndImage`, raster pattern and scan operators.
- Data type tags for unsigned/signed integers, real values, arrays, xy pairs, boxes, attribute tags, and data length markers.

The numeric order is intentionally protocol-defined; the driver writes these enum values directly as bytes.
