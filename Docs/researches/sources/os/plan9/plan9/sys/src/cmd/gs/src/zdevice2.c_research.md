# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdevice2.c

Implements Level 2 page-device operators and wrappers around graphics-state save/restore operations.

Page-device query/setup operators:
- `.currentshowpagecount`
- `.currentpagedevice`
- `.setpagedevice`
- `.callinstall`
- `.callbeginpage`
- `.callendpage`

It replaces earlier implementations of `copy`, `gsave`, `save`, `gstate`, `currentgstate`, `grestore`, `grestoreall`, `restore`, and `setgstate` when page-device behavior requires PostScript callouts.

`save_page_device()` detects when a page-device dictionary must be created before saving graphics state. `restore_page_device()` detects when restore-like operations need to reapply page-device state and temporarily unlocks safety params when dictionaries differ.

`push_callout()` pushes executable names such as `%gsavepagedevice`, `%restorepagedevice`, and `%setgstatepagedevice` onto the execution stack.

The file exports `z2copy()` for FunctionType 4 handling and delegates gstate copying to `z2copy_gstate()` when ordinary `copy` fails on a gstate object.

Registered as Level 2 replacements in `zdevice2_l2_op_defs`.
