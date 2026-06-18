# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zicc.c

## Purpose
Implements the LanguageLevel 3 `.seticcspace` operator for ICCBased color spaces.

## Key Functions
- `zseticcspace()` validates an ICC color-space dictionary, creates a `CIEICC` color space, loads the profile, caches CIE conversion data, and installs the space.

## Important Behavior
- Requires dictionary key `N` and readable `DataSource` file.
- The current color space becomes the ICC alternate space and must be allowed as an alternate.
- Rejects an ICCBased current alternate to avoid nested ICC spaces.
- Optional `Range` is validated for monotonic min/max pairs and stored in ICC info.
- Uses stream read/write IDs as the profile file identifier.

## Research Notes
File/stream use is for ICC profile data sources, not OS filesystem implementation.
