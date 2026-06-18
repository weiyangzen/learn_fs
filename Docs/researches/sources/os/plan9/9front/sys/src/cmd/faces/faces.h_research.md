# File Research: sources/os/plan9/9front/sys/src/cmd/faces/faces.h

## Purpose
Declares shared data structures and functions for the `faces` mail notification program.

## Key Elements
Defines face string slots (`Suser`, `Sdomain`, `Sshow`, `Sdigest`), `Facesize` as 48, `Face` runtime records, and cached `Facefile` image records. Exposes mailbox globals and cross-file functions for plumbing, lookup, rendering, deletion, allocation, and mailbox registration.

## Dependencies
Requires Plan 9 draw `Image`, time `Tm`, and the implementation files in `faces`.

## Behavior/Risks
The structures share ownership across UI and image-cache code: `Face.bit` usually aliases `Facefile.image`, and `freeface` must distinguish aliases from separately allocated fallback images.
