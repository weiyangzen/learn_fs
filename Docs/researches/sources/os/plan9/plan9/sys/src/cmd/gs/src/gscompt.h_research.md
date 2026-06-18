# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscompt.h

## Purpose
Abstract client interface for Ghostscript compositing objects.

## Key Contents
- Documents compositing as occurring after color correction and before halftoning.
- Forward-declares `gs_composite_t`.
- Declares `gs_composite_id`.

## Important Details
- Concrete compositing subclasses are expected to provide default implementations for devices without optimized compositing support.
- Compositing objects carry unique IDs for cache lookup and equality testing.

## Dependencies
Requires `gs_id` type from the surrounding Ghostscript type environment.

## Research Notes
This is an abstract contract header only; concrete RasterOp/alpha compositing code is elsewhere.
