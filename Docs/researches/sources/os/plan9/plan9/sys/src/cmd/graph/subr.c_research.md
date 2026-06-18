# File Research: sources/os/plan9/plan9/sys/src/cmd/graph/subr.c

This file implements `putnum`, the helper declared by `iplot.h`. It prints grouped coordinate arrays in braces for plot commands that need a sequence of points, emitting pairs of doubles and line breaks after alternating entries.

It is a small serialization helper for spline/polygon/fill macros.
