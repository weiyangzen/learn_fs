# File Research: sources/os/plan9/9front/sys/src/cmd/samterm/flayer.h

`flayer.h` defines samterm's layer interface.

`Flayer` wraps a `Frame` with global text origin, selection range, click time, text loading callback, user fields, full rectangle, scroll rectangle, last scroll-bar rectangle, and visibility state.

It declares all layer lifecycle, geometry, selection, refresh, resize, insertion/deletion, preparation, and hit-testing functions.

The header also defines UI constants for click timing, margins, scroll width, gap, command/main color arrays, and the global selection anchor `sel`.
