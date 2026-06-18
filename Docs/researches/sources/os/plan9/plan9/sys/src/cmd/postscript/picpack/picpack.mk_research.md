# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/picpack/picpack.mk

Makefile for the `picpack` PostScript/troff preprocessor.

Key responsibilities:
- Defines build/install variables and common include directory.
- Builds `picpack` from `picpack.o` plus common `glob`, `misc`, and `tempnam` objects.
- Installs binary and man page with ownership/mode setup.
- Delegates common object builds to `../common/common.mk`.

Notable behavior:
- `changes` rewrites defaults in the makefile using `sed`.
