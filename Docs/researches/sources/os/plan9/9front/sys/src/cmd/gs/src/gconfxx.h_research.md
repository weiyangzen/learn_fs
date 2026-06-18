# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gconfxx.h

## Scope

Generated configuration inventory equivalent to `gconfig.h`.

## Key Behavior

- Lists the same configured resources as `gconfig.h`: compositors, devices, operators, PostScript files, IODevices, emulators, function types, image types, image classes, and init procedures.
- Intended for macro-driven inclusion by configuration table builders or alternate build paths.
- Contains the same Plan 9, printer, image/PDF/PostScript, FAPI, and interpreter-resource entries.

## Dependencies

Used through conditional macro definitions by Ghostscript build/configuration code.

## Risks And Invariants

- Generated content must stay synchronized with the configured build.
- The file has no traditional declarations unless macros like `device_`, `oper_`, or `psfile_` are defined by the includer.
