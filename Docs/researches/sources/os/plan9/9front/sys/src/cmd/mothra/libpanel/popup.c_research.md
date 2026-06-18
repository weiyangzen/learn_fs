# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/popup.c

Implements a popup container that temporarily displays one of three panels based on mouse button.

Key behavior:
- On button press, selects a popup panel, packs it, positions it near the pointer within bounds, saves covered pixels, makes it visible, and draws it.
- Routes mouse events into the selected popup panel while active.
- On release, restores saved pixels and hides the popup.
- Uses popup priority so it can win hit testing.

Important dependencies: `plpack`, `plmove`, `pl_invis`, `plmouse`, draw image save/restore.

Notable risks:
- Save image allocation failure leaves restoration unavailable.
- Popup state is button-specific (`DOWN1/2/3`) and tied to mouse button bitmasks.
