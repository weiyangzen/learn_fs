# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/macos_carbon_d_pre.h

`macos_carbon_d_pre.h` is a CodeWarrior prefix header for the debug Carbon target. It defines `__CARBON__` and `DEBUG 1`.

It is selected by `macgenmcpxml.sh` for the `GhostscriptLib Carbon (Debug)` target. Its only behavioral effect is compile-time selection of Carbon APIs and Ghostscript verbose/debug code paths.
