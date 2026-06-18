# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpxat.h

This header defines PCL XL attribute IDs as `px_attribute_t`.

It includes attributes for:
- Color and palette data: `pxaPaletteDepth`, `pxaColorSpace`, `pxaRGBColor`, `pxaGrayLevel`, `pxaPaletteData`.
- Page/media controls: `pxaMediaSize`, `pxaMediaSource`, `pxaMediaType`, `pxaOrientation`, `pxaPageCopies`, duplex/simplex fields.
- Path and drawing state: `pxaBoundingBox`, `pxaEndPoint`, `pxaFillMode`, `pxaLineCapStyle`, `pxaLineJoinStyle`, `pxaMiterLength`, `pxaLineDashStyle`, `pxaPenWidth`, `pxaClipRegion`, `pxaClipMode`.
- Raster/image fields: `pxaColorDepth`, `pxaColorMapping`, `pxaCompressMode`, `pxaDestinationSize`, `pxaSourceHeight`, `pxaSourceWidth`, `pxaStartLine`, `pxaBlockByteLength`, `pxaNumberOfScanLines`.
- Data/source/session fields: `pxaCommentData`, `pxaDataOrg`, `pxaMeasure`, `pxaSourceType`, `pxaUnitsPerMeasure`, stream fields, and error reporting.
- Font/text fields: `pxaCharAngle`, `pxaCharCode`, `pxaCharDataSize`, `pxaCharSize`, `pxaFontHeaderLength`, `pxaFontName`, `pxaFontFormat`, `pxaSymbolSet`, `pxaTextData`, writing mode, spacing data, and bold value.

The enum mirrors numeric PCL XL protocol attribute IDs, including comments for version-specific values.
