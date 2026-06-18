# File Research: sources/os/plan9/plan9/sys/src/cmd/grap/ticks.c

This file implements tick and grid generation for `grap`. It stores explicit tick values/labels, side selections, tick direction/length, automatic tick side state, and grid descriptors.

`ticks` updates automatic tick policy based on explicit lists, side selection, `in/out`, and `off`. `setauto`, `autoside`, and `autolog` compute automatic linear or log tick quantization/ranges for the default coordinate object.

`do_autoticks`, `iterator`, `ticklist`, `print_ticks`, and `maketick` generate tick marks and labels. `gridlist` reuses tick machinery to emit full grid lines, with optional descriptors and side-specific tick suppression.

Log axes validate positive tick values before transforming them.
