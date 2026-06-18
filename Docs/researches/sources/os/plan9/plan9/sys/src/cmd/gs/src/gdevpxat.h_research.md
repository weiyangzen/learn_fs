# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpxat.h

This header defines PCL XL attribute IDs as `px_attribute_t`. The numeric values are protocol identifiers that the driver writes directly to output streams.

Covered attribute groups include:
- Color and palette data: `pxaPaletteDepth`, `pxaColorSpace`, `pxaRGBColor`, `pxaGrayLevel`, and `pxaPaletteData`.
- Page and media controls: `pxaMediaSize`, `pxaMediaSource`, `pxaMediaType`, `pxaOrientation`, `pxaPageCopies`, simplex/duplex fields, and destination fields.
- Path and drawing state: `pxaBoundingBox`, `pxaEndPoint`, `pxaFillMode`, `pxaLineCapStyle`, `pxaLineJoinStyle`, `pxaMiterLength`, `pxaLineDashStyle`, `pxaPenWidth`, `pxaClipRegion`, and `pxaClipMode`.
- Raster/image fields: `pxaColorDepth`, `pxaColorMapping`, `pxaCompressMode`, `pxaDestinationSize`, `pxaSourceHeight`, `pxaSourceWidth`, `pxaStartLine`, `pxaBlockByteLength`, and `pxaNumberOfScanLines`.
- Data/session fields: `pxaCommentData`, `pxaDataOrg`, `pxaMeasure`, `pxaSourceType`, `pxaUnitsPerMeasure`, stream fields, and error reporting.
- Font/text fields: `pxaCharAngle`, `pxaCharCode`, `pxaCharDataSize`, `pxaCharSize`, `pxaFontHeaderLength`, `pxaFontName`, `pxaFontFormat`, `pxaSymbolSet`, `pxaTextData`, writing mode, spacing data, and bold value.

Comments identify attributes introduced in later PCL XL versions. This is a protocol vocabulary header for `gdevpx.c` and `gdevpxut.c`.
