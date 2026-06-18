# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfunc3.c

## Role

Implementation of LanguageLevel 3 function types: exponential interpolation, 1-input stitching, and internal arrayed-output functions.

## Main Data

Defines concrete function records for `ElIn`, `1ItSg`, and `AdOt`, helper routines to free and scale arrays of subsidiary functions, and GC descriptors from `gsfunc3.h`.

## Control Flow

Exponential functions clamp input, compute `arg^N`, interpolate between `C0` and `C1`, clamp to Range, and are always monotonic when valid. Stitching functions select a subfunction based on Bounds, encode the input into that subfunction’s domain, and evaluate it; monotonicity delegates to the selected segment when the tested interval does not cross a stitch. Arrayed-output functions evaluate multiple one-output subfunctions and assemble their outputs, handling overlapping input/output buffers for small input counts.

## Dependencies

Uses function common helpers, Ghostscript parameter lists, math wrappers, streams, and subsidiary function APIs.

## Notes

Arrayed-output Domain is computed as the intersection of subfunction domains; comments note this is tailored to shadings and similar dictionaries.
