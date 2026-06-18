# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iimage2.h

Declares Level 2 image support for images without explicit source data.

Key points:
- Declares `process_non_source_image`.
- Comments note this is not used by standard Level 2 but needed by DPS/NeXT-related modules.
- Takes interpreter context, common image parameters, and a client name.

Dependencies and interactions:
- Exported by `zimage2.c`.
- Used by `zdps.c` and `zdpnext.c`.

Research relevance:
- Small compatibility hook for non-standard image processing paths.
