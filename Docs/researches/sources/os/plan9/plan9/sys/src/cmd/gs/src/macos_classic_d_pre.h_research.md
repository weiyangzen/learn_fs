# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/macos_classic_d_pre.h

`macos_classic_d_pre.h` is a CodeWarrior prefix header for the debug classic Mac OS target. It defines `DEBUG` without a numeric value.

It is selected for `GhostscriptLib PPC (Debug)` by `macgenmcpxml.sh`. Unlike the Carbon debug prefix, it does not define `__CARBON__`, so it leaves compilation on the classic Mac OS path.
