# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/fonts.h

Static font path list for Abaco.

Key contents:
- Lists Lucida Sans normal, italic, and bold Unicode bitmap fonts at several sizes.
- Lists fixed-width Unicode bitmap fonts at several sizes.

Dependencies:
- Included by `util.c` inside font path setup.

Notable risks:
- Paths are hard-coded to Plan 9 `/lib/font/bit/...`; missing fonts affect rendering.
