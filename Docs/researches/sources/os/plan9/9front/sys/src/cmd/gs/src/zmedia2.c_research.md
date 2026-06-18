# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zmedia2.c

## Purpose
Implements Level 2 media matching helpers for `setpagedevice`, including `.matchmedia` and `.matchpagesize`.

## Key Functions
- `zmatchmedia()` selects a medium from input attributes based on requested attributes, policies, priority, orientation, and media position.
- `zmatchpagesize()` exposes page-size matching directly.
- `zmatch_page_size()` converts PostScript arrays to geometric values.
- `match_page_size()` matches requested size against fixed or ranged media.
- `make_adjustment_matrix()` computes rotation, scaling, and centering adjustment matrices.

## Important Behavior
- Null input attributes short-circuit to `null true`.
- PageSize matching tolerates differences within 5 units and can rotate dimensions.
- Policy values control exact, nearest, next-larger, scaling, and forced-request behavior.
- Media-position mismatch adds a small penalty.
- Priority arrays break ties among otherwise matching media.

## Research Notes
Page-device/media selection logic, not file or storage logic.
