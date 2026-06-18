# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gslparam.h

Defines line cap and line join enumerations. Standard PostScript values are present, plus Ghostscript extensions: triangle cap, no join, triangle join, and unknown sentinels.

`gs_line_cap_max` is 3, so `gs_cap_unknown` is not accepted by normal setters. `gs_line_join_max` is 4, so triangle join is accepted while unknown is not.
