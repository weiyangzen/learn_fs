# File Research: sources/local-fs/xfsdump/common/media_rmvtape.h

## Role

This header defines removable-tape media-specific header and context structures.

It is used by the `rmvtape` media strategy to interpret the `media_hdr_t.mh_specific` region.

## Structures

`media_rmvtape_spec_t` overlays the 128-byte media-specific header area. It contains:

- `mrmv_flags`
- padding to fill the reserved region

`media_context_t` records media/dump UUIDs and media/dump labels for the removable-tape strategy.

## Flags And Capability Macros

- `RMVMEDIA_TERMINATOR_BLOCK` marks a terminator block.
- `TERM_IS_SET()` checks that flag.
- `CAN_OVERWRITE()`, `CAN_APPEND()`, and `CAN_BSF()` test drive capabilities needed by removable tape behavior.
