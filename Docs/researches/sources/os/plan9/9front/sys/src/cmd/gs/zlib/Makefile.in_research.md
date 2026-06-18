# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/Makefile.in

## Purpose
Template Makefile used by the zlib `configure` script.

## Key Elements
Contains the same build variables, object lists, targets, install rules, clean rules, and generated dependency comments as `Makefile`.

## Behavior/Risks
`configure` rewrites selected assignment lines such as `CC`, `CFLAGS`, `CPP`, `LDSHARED`, `LIBS`, shared-library names, install paths, and `LDFLAGS` into `Makefile`. Since this checked-in `Makefile.in` already matches `Makefile`, it also serves as a reset target for `distclean`.

## Dependencies
Used by `configure` through `sed` substitution and by `make distclean` through `cp -p Makefile.in Makefile`.
