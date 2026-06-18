# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscompt.h

## Role

`gscompt.h` defines the abstract compositing-object type used near the end of the Ghostscript rendering pipeline.

This is rendering pipeline infrastructure, not filesystem code.

## Public API

- `typedef struct gs_composite_s gs_composite_t`
- `gs_composite_id`

## Design Notes

The comments define compositing as occurring after color correction and before halftoning. Concrete compositing implementations are expected to provide default device implementations when target devices lack optimized support.

Compositing objects carry unique IDs for cache lookup and equality testing, similar to halftones and transfer functions.

## Dependencies

Uses `gs_id` from Ghostscript base types.

## Notable Risks

This header is intentionally abstract; concrete behavior is defined by subclasses elsewhere.
