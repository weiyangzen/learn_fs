# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zimage3.c

## Purpose
Implements LanguageLevel 3 masked image operators `.image3` and `.image4`.

## Key Functions
- `zimage3()` parses ImageType 3 data/mask dictionaries and interleave rules.
- `zimage4()` parses ImageType 4 color-key mask data.
- Both route completed image structures through `zimage_setup()`.

## Important Behavior
- ImageType 3 requires `DataDict`, `MaskDict`, and `InterleaveType` 1..3.
- `MaskDict` DataSource presence must match `InterleaveType == 3`.
- Multiple data sources are only allowed for ImageType 3 when interleaved type 3 is used.
- ImageType 4 accepts `MaskColor` as component values or component ranges and clamps impossible matches.

## Research Notes
Extends the common image machinery in `zimage.c` for LL3 masked-image forms.
