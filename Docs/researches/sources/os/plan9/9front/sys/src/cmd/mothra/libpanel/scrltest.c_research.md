# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/scrltest.c

A small test/demo program for libpanel list scrolling.

Key behavior:
- Builds a root group with a scrollable generated list, a message label, and save/revert/done buttons.
- `save` captures the list scroll position; `revert` restores it.
- `ereshaped()` repacks and redraws the panel tree on window reshape.
- Main event loop sends mouse events to the root panel.

Important dependencies: libpanel, old Plan 9 draw/event APIs.

Notable risks:
- Uses older draw API names (`binit`, `bitblt`, `screen.ldepth`) that may be compatibility-specific.
