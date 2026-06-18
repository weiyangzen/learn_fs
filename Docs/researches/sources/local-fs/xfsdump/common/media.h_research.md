# File Research: sources/local-fs/xfsdump/common/media.h

## Role

This header defines the common media-file header layout and media strategy IDs.

The header is embedded in the drive header's upper area and is read/written at media-file boundaries.

## `media_hdr_t`

The fixed media header records:

- current and previous media labels
- current and previous media UUIDs
- media object index
- media file index
- dump file index
- dump/media combined indexes
- dump index within media
- media strategy ID
- strategy-specific 128-byte area
- upper-layer private area

`MEDIA_HDR_SZ` is derived from the drive header upper area size, and `media.c` asserts that the layout fits.

## Terminator Macros

`MEDIA_TERMINATOR_CHK()` and `MEDIA_TERMINATOR_SET()` mark media files as terminators using the first byte of `mh_specific`. This is noted as an artifact of the original removable-tape strategy.

## Strategy IDs

- `MEDIA_STRATEGY_SIMPLE`
- `MEDIA_STRATEGY_RMVTAPE`
