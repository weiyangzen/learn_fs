# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttconfig.h

Purpose: FreeType-derived TrueType configuration settings adapted for Ghostscript.

Key contents:
- Includes `ttconf.h`.
- Leaves debug and one’s-complement support disabled.
- Leaves `_GNUC_LONG64_` disabled by default.
- Defines `ALIGNMENT 8`.
- Enables `SECURE_COMPUTATIONS`.
- Enables `IGNORE_FILL_FLOW`.
- Defines `Print` through `vfprintf` unless an external print function is configured.
- Defines endian constants and `FT_BYTE_ORDER`; enables `LOOSE_ACCESS` for suitable big-endian unaligned-access environments.
- Disables thread-safe/reentrant flags and static interpreter/raster flags.
- Enables `TT_EXTEND_ENGINE`.

Dependencies: `ttconf.h`, standard `vfprintf` availability through surrounding includes.

Integration notes: controls TrueType arithmetic, raster, and table-management compilation choices.

Risks: non-thread-safe default is explicit; shared interpreter use must be serialized externally.
