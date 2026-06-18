# File Research: sources/os/plan9/9front/sys/src/cmd/samterm/icons.c

`icons.c` defines samterm cursor bitmaps and one shared color.

The cursors are `bullseye` for selecting windows for menu actions, `deadmouse` for snarf exchange/wait states, and `lockarrow` for host-locked input. Each cursor provides Plan 9 cursor offset, clear mask, and set mask.

`iconinit` allocates `darkgrey`, a 1x1 image used elsewhere by the terminal UI.
