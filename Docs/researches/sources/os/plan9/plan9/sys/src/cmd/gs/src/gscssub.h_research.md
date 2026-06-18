# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscssub.h

## Role

`gscssub.h` documents and exposes Ghostscript’s library-level color-space substitution API.

## Semantics

When device `UseCIEColor` is false, DeviceGray/RGB/CMYK behavior is unchanged. When true, selected operations may substitute configured color spaces for implied device spaces:

- `gs_setgray`, `gs_setrgbcolor`, `gs_sethsbcolor`, `gs_setcmykcolor`
- `gs_current_Device{Gray,RGB,CMYK}_space`

The comments clarify differences from PostScript `UseCIEColor`: substitution is visible to `gs_currentcolorspace`, does not affect explicit `gs_setcolorspace`, and does not alter image or shading `ColorSpace` members. Traditional color accessors still report values in the pre-substitution device color model.

## API

- `gs_setsubstitutecolorspace(...)`
- `gs_currentsubstitutecolorspace(...)`
- fast internal accessors for current DeviceGray, DeviceRGB, and DeviceCMYK spaces

Passing `NULL` to `gs_setsubstitutecolorspace` clears a substitution.

## Dependencies

Includes `gscspace.h` and relies on `gs_state`, `gs_color_space`, and `gs_color_space_index`.

## Risks

The header notes that substitutions survive ordinary `grestore` and `setgstate`; copied graphics states share substitutions. This is intentional but can surprise callers expecting normal graphics-state stack behavior.
