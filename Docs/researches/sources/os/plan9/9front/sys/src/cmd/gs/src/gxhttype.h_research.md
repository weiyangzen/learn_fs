# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxhttype.h

## Role

`gxhttype.h` defines the `gs_halftone_type` enumeration used by Ghostscript client and graphics-state halftone structures.

This is imaging/halftone infrastructure, not filesystem code.

## Enumerated Types

- `ht_type_none`
- `ht_type_screen`
- `ht_type_colorscreen`
- `ht_type_spot`
- `ht_type_threshold`
- `ht_type_threshold2`
- `ht_type_multiple`
- `ht_type_multiple_colorscreen`
- `ht_type_client_order`

## Notes

- `ht_type_threshold2` is documented as extended Type 3 with 8- or 16-bit samples, bytestring thresholds, and one or two rectangles.
- `ht_type_multiple_colorscreen` represents Type 5 halftone dictionaries created from Type 2 or Type 4 halftone dictionaries.

## Notable Risks

- The enum is shared across halftone unions; adding or reordering values would require auditing all switch and serialization users.
