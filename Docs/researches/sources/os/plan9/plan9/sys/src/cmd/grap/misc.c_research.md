# File Research: sources/os/plan9/plan9/sys/src/cmd/grap/misc.c

This file contains general `grap` utility state and helpers. It stores numeric lists, current text justification/size operators, and provides `savenum`, `setjust`, `setsize`, `tostring`, `lookup`, variable get/set, point construction, and attribute list creation/freeing.

`range` and `halfrange` update coordinate object min/max ranges unless a coordinate bound was explicit. `setvar` special-cases `pointsize` to update global text sizing.

`slprint`, `juststr`, and `sprntf` convert string/attribute lists into `pic` text box output, justification suffixes, and formatted string values.
