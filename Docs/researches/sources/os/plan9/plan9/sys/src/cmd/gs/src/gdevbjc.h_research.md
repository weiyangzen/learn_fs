# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbjc.h

Configuration header for older Canon BJC printer drivers, especially BJC-600 and BJC-800 style devices.

Key contents:
- Defines driver names and version strings for `bjc600` and `bjc800`.
- Defines print-limit and margin constants, including optional recommended/tight margin modes.
- Defines BJC head-row count and media-weight thresholds.
- Provides margin macros for letter, A4, and A3.
- Defines public parameter names such as `ManualFeed`, `DitheringType`, `MediaType`, `MediaWeight`, `PrintQuality`, `ColorComponents`, `PrintColors`, and `MonochromePrint`.
- Enumerates media types, dithering modes, quality modes, printable color bitmasks, and base resolutions.
- Supplies generic defaults and per-model defaults for media, quality, dithering, manual feed, monochrome mode, resolution, bits per pixel, component count, print colors, and media weight.

Notable dependencies:
- This is a macro-only header and does not include other headers directly.

Research notes:
- There is a typo/inconsistency in the inner include guard: `#ifndef _GDEV_BJC_H` is followed by `#define _GDEV_CDJ_H`, so `_GDEV_BJC_H` is never actually defined. The outer `gdevbjc_INCLUDED` guard prevents repeat inclusion in normal use, but the inner guard is ineffective.
- The defaults intentionally allow compile-time override by defining `BJC_DEFAULT_*` or model-specific `BJC600_DEFAULT_*`/`BJC800_DEFAULT_*` macros before inclusion.
- The file distinguishes `ColorComponents` from `BitsPerPixel`, warning that changing one requires a compatible change to the other.
