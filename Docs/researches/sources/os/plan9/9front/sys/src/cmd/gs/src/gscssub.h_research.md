# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscssub.h

This header declares the color-space substitution API and explains how it differs from PostScript `UseCIEColor`.

Key behavior from the comments:
- Substitution is active only when the current device has `UseCIEColor` true.
- It affects library color setters such as `gs_setgray`, `gs_setrgbcolor`, `gs_sethsbcolor`, and `gs_setcmykcolor`.
- Unlike PostScript `UseCIEColor`, substitution is visible to `gs_currentcolorspace`.
- It does not affect explicit `gs_setcolorspace` or image/shading color-space members.
- Graphics states copied by `gsave`, `gstate`, `currentgstate`, or `copygstate` share substitutions; ordinary `grestore` and `setgstate` do not undo them.

Declared API:
- `gs_setsubstitutecolorspace`
- `gs_currentsubstitutecolorspace`
- Fast internal accessors for current DeviceGray/RGB/CMYK spaces.
