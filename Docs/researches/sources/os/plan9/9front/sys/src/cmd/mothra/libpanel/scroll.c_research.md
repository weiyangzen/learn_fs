# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/scroll.c

Provides generic scroll linkage and scroll-state helpers.

Key behavior:
- `plscroll()` links a scrollee panel to optional x/y scroller panels and back-links scrollers to their scrollee.
- `plgetscroll()` returns a panel’s `Scroll` state.
- `plsetscroll()` drives a panel’s scroll callback to restore x/y positions.

Important dependencies: panel scroll callback methods.

Notable risks:
- `plsetscroll()` only scrolls axes with nonzero saved size.
