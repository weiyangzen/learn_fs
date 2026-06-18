# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdsp.h

## Role
`gdevdsp.h` is the public callback contract for the Ghostscript DLL/shared-library `display` device implemented in `gdevdsp.c`.

## Contents
- Defines display callback ABI versions: V2.0 current and V1.0 legacy.
- Defines `DisplayFormat` bitfields for color model, alpha/unused component placement, depth, component ordering/endian-style packing, top-first versus bottom-first row order, native 555/565 RGB, and row alignment.
- Declares `struct display_callback_s`, whose function pointers cover open, preclose, close, presize, size, sync, page, update, optional memory allocation/free, and V2 separation mapping.
- Declares `struct display_callback_v1_s`, identical except without `display_separation`.

## Behavior Contract
- The documented setup order is `gsapi_new_instance`, `gsapi_set_display_callback`, then `gsapi_init_with_args`.
- `DisplayHandle` is passed back to all callbacks and may be supplied as a string for pointer-width safety.
- Clients must not read the image buffer before first sync, between presize and size, or after preclose.
- Typical callback sequence is open, presize, memalloc, size, sync/page, optional resize cycles, then preclose, memfree, close.

## Risks and Notes
- Header-only ABI surface; misuse affects embedding applications directly.
- The header states alpha-first and alpha-last are not implemented, matching the implementation's range checks.
- Separation callbacks are optional and guarded by callback version checks in `gdevdsp.c`.
