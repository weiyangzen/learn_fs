# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/ctx/pch.h

## Purpose
Precompiled header for the `ctx` minifilter sample. It centralizes common system and project includes and enables strict compiler warnings.

## Key Contents
- Include guard: `__CTX_PCH_H__`
- Warning pragmas promoted to errors:
  - `4100` unreferenced formal parameter
  - `4101` unreferenced local variable
  - `4061` missing enum case in switch
  - `4505` unreferenced local function
- Includes:
  - `<fltKernel.h>`
  - `<dontuse.h>`
  - `<suppress.h>`
  - `"CtxStruc.h"`
  - `"CtxProc.h"`

## Notable Detail
The closing directive is written as `#endif __CTX_PCH_H__`, which places extra tokens after `#endif`. This is accepted by some C preprocessors with a warning, but the conventional form would be `#endif // __CTX_PCH_H__`.

## Research Notes
This file intentionally makes unused parameters and locals build-breaking unless explicitly marked with `UNREFERENCED_PARAMETER`, which explains the frequent annotations in the implementation files.
