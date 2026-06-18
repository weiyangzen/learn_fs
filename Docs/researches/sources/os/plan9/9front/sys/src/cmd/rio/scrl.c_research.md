# File Research: sources/os/plan9/9front/sys/src/cmd/rio/scrl.c

Scrollbar drawing and mouse-scroll behavior for `rio` windows.

`wscrdraw()` computes thumb position from `org`, visible chars, and total runes, drawing through a reusable temporary image. `wscroll()` handles button-specific scrolling modes: page/back line scrolling, absolute thumb dragging, and forward scrolling with debounce timers.

`freescrtemps()` releases cached scroll drawing storage after screen changes.
