# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/button.c

Implements libpanel buttons, check buttons, radio buttons, menu buttons, and menus.

Key behavior:
- Draws button variants with relief boxes, optional check/radio marks, and centered icons/text.
- Mouse handling tracks down/up/out state and invokes callbacks on release.
- Radio buttons clear sibling radio buttons in the same parent.
- `plmenu()` builds a group of menu buttons from an icon array and callback.
- `plsetbutton()` programmatically sets check/radio state.

Important dependencies: `panel.h`, `pldefs.h`, drawing primitives from `draw.c`.

Notable risks:
- Radio grouping is implicit by parent and widget type.
- Callback signatures differ between normal buttons, check/radio buttons, and menu items.
