# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gconfxx.h

Generated configuration manifest matching `gconfig.h`.

Key points:
- Contains the same generated component entries as `gconfig.h`.
- Macro-guarded entries cover compositor types, devices, operator sets, initialization PostScript files, IODevices, emulators, function types, image types, init procedures, and image classes.
- Used as an alternate generated config include when selected by build macros.

Dependencies and interactions:
- Compatible with `gconf.h`’s `GCONFIG_H` override mechanism.

OS/filesystem relevance:
- Same as `gconfig.h`: includes IODevices and init/library file names.
