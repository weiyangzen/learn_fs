# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postreverse/postreverse.h

Local page-offset structure for `postreverse`.

Contents:
- Defines `Pages` with:
  - `long start`
  - `long stop`
  - `int empty`
- Declares `char *copystdin()`.

Role:
- Supplies the page table entry used by `postreverse.c` to record byte ranges for each page and dummy-page markers.

Risks and quirks:
- No table size is defined here; `postreverse.c` hardcodes `pages[1000]`.
