# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbjc.h

## Purpose
Defines constants and defaults for older Canon BJC printer drivers, especially BJC-600 and BJC-800 style devices.

## Contents
- Driver names and version strings:
  - `BJC_BJC600`
  - `BJC_BJC800`
- Hardware margin/limit constants, including lower-limit modes controlled by `USE_RECOMMENDED_MARGINS` and `USE_TIGHT_MARGINS`.
- Media weight thresholds.
- Print-head row count.
- Letter/A4/A3 margin macros.
- Public option names such as `ManualFeed`, `DitheringType`, `MediaType`, `PrintQuality`, `ColorComponents`, `PrintColors`, and `MonochromePrint`.
- Enumerated integer values for media types, dithering modes, quality modes, and color component masks.
- Resolution constants based on 90 dpi increments.
- Generic defaults and BJC600/BJC800-specific default overrides.

## Integration Role
This is a configuration header, not an implementation file. It centralizes compile-time defaults for Canon BJC drivers that include it.

## Notes
- Header guard has an apparent typo/inconsistency: `#ifndef _GDEV_BJC_H` followed by `#define _GDEV_CDJ_H`, while the closing comment says `_GDEVBJC_H`.
- Defaults are designed to be overridden by preprocessor defines at build time.
