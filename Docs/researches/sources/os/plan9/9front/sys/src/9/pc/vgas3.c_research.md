# File Research: sources/os/plan9/9front/sys/src/9/pc/vgas3.c

## Role

VGA support module for S3 adapters, including bank switching, linear aperture setup, hardware cursor support, blanking, ViRGE acceleration, and delegation to the Savage acceleration module.

## Main Interfaces

- Exports `VGAdev vgas3dev` named `s3`.
- Exports `VGAcur vgas3cur` named `s3hwgc`.
- Main routines: `s3page`, `s3linear`, `s3enable`, `s3disable`, `s3load`, `s3move`, `s3drawinit`, `s3blank`, `hwfill`, and `hwscroll`.

## Key Behavior

- Validates S3 PCI vendor `0x5333` for linear setup and uses `vgalinearpci()` for PCI framebuffer mapping.
- Implements bank switching through S3 CRT registers, with different bit layouts for older chips and higher-depth modes.
- Loads a Microsoft-Windows-format hardware cursor image into display memory and handles offscreen positioning with cursor offsets.
- Works around hardware timing by avoiding cursor toggles during selected vertical/horizontal blank intervals.
- Provides FIFO/idle wait helpers for the S3 graphics engine and optional ViRGE solid fill/screen scroll acceleration.
- `s3drawinit()` reads S3 chip ID registers, installs blanking, enables ViRGE acceleration for known chips, and calls external `savageinit()` for Savage/ProSavage/SuperSavage IDs.

## Dependencies And Assumptions

- Depends on S3 extended VGA registers, PCI BAR layout, and chip IDs shared with `vgasavage.c`.
- Some acceleration paths are deliberately disabled for unknown ViRGE variants because FIFO depth is unknown.

## Research Notes

- This file is both an S3 driver and the dispatch point into `vgasavage.c` for newer S3-derived chips.
