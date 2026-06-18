# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/pulldown.c

Implements pulldown buttons and menubars.

Key behavior:
- Draws a button label/icon and, on press, packs a supplied panel on a chosen side.
- Saves covered pixels, shows the pulldown panel, routes events into it, then restores and hides it when closed.
- Supports side placement north/south/east/west/center.
- `plmenubar()` builds a group of pulldown buttons from varargs.

Important dependencies: `plpack`, `plmove`, `pl_invis`, `plmouse`, draw save/restore.

Notable risks:
- Pull panel is external; caller manages its lifetime and content.
- Varargs API requires icon/panel pairs terminated by nil.
