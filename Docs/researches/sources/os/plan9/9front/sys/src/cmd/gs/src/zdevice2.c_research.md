# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zdevice2.c

Implements Level 2 page-device operators and wrappers for save/restore-sensitive graphics-state operations.

Key behavior:
- Adds `.currentshowpagecount`, `.currentpagedevice`, `.setpagedevice`, `.callinstall`, `.callbeginpage`, and `.callendpage`.
- Replaces `copy`, `gsave`, `save`, `gstate`, `currentgstate`, `grestore`, `grestoreall`, `restore`, and `setgstate` with page-device-aware wrappers.
- Detects when saving or restoring graphics state requires creating or restoring a pagedevice dictionary.
- Uses `push_callout` to invoke PostScript procedures such as `%gsavepagedevice`, `%restorepagedevice`, and `%setgstatepagedevice`.
- Temporarily unlocks `LockSafetyParams` when a restore path must apply different page-device parameters.

Dependencies:
- Bridges device/page procedures, interpreter save/restore machinery, gstate objects, and dictionary/name lookup.

Research notes:
- This file is policy glue: it keeps C graphics-state operations compatible with PostScript pagedevice semantics.
