# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gconfig.h

## Scope

Generated Ghostscript configuration inventory.

## Key Behavior

- Lists configured compositors, devices, operators, PostScript initialization files, IODevices, emulators, function types, image types, image classes, and init procedures behind conditional macros.
- Includes Plan 9 relevant devices such as `gs_plan9_device` and `gs_plan9bm_device`, along with printer, image, PDF/PostScript, and nullpage devices.
- Enumerates interpreter operator sets for PostScript levels, PDF support, filters, font formats, color spaces, DPS, FAPI, and image handling.
- Lists init/runtime PostScript resources such as `gs_init.ps`-related support files, PDF files, CMap/CID files, Type 1/42 files, and FAPI/PDF writer support.

## Dependencies

Consumed by `gconf.h` and table-building sources through macro redefinition.

## Risks And Invariants

- Generated file; manual edits would likely be overwritten.
- Each item only emits when the including source defines its corresponding macro.
- Length arguments in `psfile_` / `emulator_` entries must match literal lengths.
