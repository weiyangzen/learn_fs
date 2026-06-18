# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscssub.c

## Role

`gscssub.c` implements library-level color-space substitution, corresponding to `.setsubstitutecolorspace` and `.currentsubstitutecolorspace`.

## Main Behavior

`gs_setsubstitutecolorspace` sets or clears substitutions for DeviceGray, DeviceRGB, and DeviceCMYK only. It validates the requested device-space index, accepts ICCBased substitutes only when their component count matches the target device space, then either allocates a private substituted color-space copy or assigns over an existing one.

If `pcs` is null, it resets a substitution to the shared default device color space.

The accessors:

- `gs_current_DeviceGray_space`
- `gs_current_DeviceRGB_space`
- `gs_current_DeviceCMYK_space`

return the substituted space only when `pgs->device->UseCIEColor` is true and a per-state substitute exists. Otherwise they return the shared default device space.

`gs_currentsubstitutecolorspace` dispatches by device color-space index.

## Dependencies

Uses graphics-state internals (`gzstate.h`), device client state (`gxdevcli.h`), color-space struct descriptors (`gxcspace.h`), and Ghostscript memory/error helpers.

## Risks

The non-ICC validation expression appears suspicious: `else if (!masks[index] && (1 << gs_color_space_get_index(pcs)))` is false for all populated mask entries, so the intended mask check is likely ineffective. Substitution state is shared across copied graphics states per the header contract, so callers should not assume ordinary `grestore` undoes substitutions.
