# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/subr.c

`subr.c` defines the global libplot environment stack `E`, active pointers `e0/e1`, color parsing, environment copy, and placeholder functions. `bcolor()` accepts named single-letter colors, numeric color-map values, raw `R` integer colors, and side-effect commands for gap/slant.

`sscpy()` copies all plotting environment fields between `penvir` structures. `idle()` and `ptype()` are stubs.
