# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/ubifs.h

## Purpose
Reduced UBIFS internal header used by `mkfs.ubifs` for image construction.

## Key Elements
Defines UBIFS LEB size limits, key union, LEB property flags, LPT node structures, LEB property statistics, zbranch/znode structures, and the subset of `struct ubifs_info` needed by the user-space mkfs path. Provides inline helpers for index node sizing and branch lookup.

## Dependencies
Uses UBIFS media constants and UBI device/volume info structures included through the mkfs header stack.

## Behavior/Risks
This is not the full kernel UBIFS state model; it is a build-time subset tailored for creating a static filesystem image. Consumers must keep it synchronized with the media format expectations used by the companion key/LPT code.
