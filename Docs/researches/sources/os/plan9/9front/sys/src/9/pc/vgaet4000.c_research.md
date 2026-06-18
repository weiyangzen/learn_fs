# File Research: sources/os/plan9/9front/sys/src/9/pc/vgaet4000.c

## Role

VGA support module for Tseng ET4000 adapters, including banked framebuffer paging and hardware cursor support.

## Main Interfaces

- Exports `VGAdev vgaet4000dev` named `et4000`.
- Exports `VGAcur vgaet4000cur` named `et4000hwgc`.
- Main routines: `et4000page`, `et4000enable`, `et4000disable`, `et4000load`, and `et4000move`.

## Key Behavior

- Programs ET4000 page registers for banked VGA memory access.
- Initializes cursor mode, cursor color, and cursor memory pointers.
- Loads Plan 9 cursor bitmap data into the ET4000 hardware cursor representation.
- Handles cursor movement with hotspot and negative-coordinate correction.

## Dependencies And Assumptions

- Depends on ET4000 extended VGA registers and standard Plan 9 VGA helper routines.
- Assumes banked display memory and reserved cursor storage.

## Research Notes

- This is a legacy non-PCI-specific module; it provides no linear aperture or acceleration hook.
