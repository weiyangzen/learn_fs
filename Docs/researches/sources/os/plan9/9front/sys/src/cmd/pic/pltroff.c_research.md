# File Research: sources/os/plan9/9front/sys/src/cmd/pic/pltroff.c

`pltroff.c` is the troff drawing backend for `pic`. It maps picture coordinates to troff inches using `space()`, `xconv()`, `yconv()`, and scaling helpers, emits `.PS`/`.PE` wrappers, line-number directives, no-fill state, and troff drawing commands.

It implements movement flushing with `\h` and `\v`, labels with justification and vertical offsets, lines, boxes, circles, ellipses, arcs, splines, arrowheads, dotted points, and PostScript fill wrappers using troff `\X` escape conventions. It also enforces maximum PostScript width/height by shrinking large pictures.
