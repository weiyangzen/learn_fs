# File Research: sources/os/plan9/9front/sys/src/9/pc/vgasavage.c

## Role

S3 Savage/ProSavage acceleration and blanking helper used by `vgas3.c`. It installs drawing callbacks for supported Savage-family chip IDs.

## Main Interfaces

- Exports `savageinit(VGAscr *scr)` for use by `s3drawinit()`.
- Main internal routines: `savagewaitidle`, `savagefill`, `savagescroll`, and `savageblank`.

## Key Behavior

- Defines Savage and SuperSavage register constants, chip IDs, command bits, and a FIFO-depth table for supported adapters.
- `savageinit()` accepts known Savage4, ProSavage, SavageIX/MX, and SuperSavage IDs, sets up MMIO/register pointers, configures pitch and bitmap descriptor state, and installs acceleration hooks.
- `savagewaitidle()` waits for engine idle using chip-specific FIFO/status behavior.
- `savagefill()` accelerates solid rectangle fill by programming foreground color, clipping, destination, dimensions, and command registers.
- `savagescroll()` accelerates screen-to-screen copies with direction handling for overlapping source/destination rectangles.
- `savageblank()` controls display blanking through sequencer/CRTC register state.

## Dependencies And Assumptions

- Depends on `vgas3.c` to identify the chip and provide `scr->id`, framebuffer, and MMIO mapping.
- Comments warn that new chip IDs must also update `savagewaitidle`, because FIFO/status behavior is chip-specific.

## Research Notes

- This file intentionally has no `VGAdev` export; it is an extension module invoked by the S3 driver.
