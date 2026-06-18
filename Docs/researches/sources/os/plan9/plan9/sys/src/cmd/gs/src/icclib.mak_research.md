# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/icclib.mak

Partial makefile for building Graeme W. Gill’s `icclib` inside Ghostscript. It expects variables such as `GLSRCDIR`, `ICCSRCDIR`, `ICCGENDIR`, and `ICCOBJDIR`.

Key build rules:
- Sets `ICCPROFVER=9809`.
- Builds `icc.$(OBJ)` from `icc.c` and ICC headers.
- Creates generated `icclib.dev` module metadata.
- Provides clean/config-clean targets for ICC generated/object files.

The makefile includes platform syntax accommodations for OpenVMS include flags.
