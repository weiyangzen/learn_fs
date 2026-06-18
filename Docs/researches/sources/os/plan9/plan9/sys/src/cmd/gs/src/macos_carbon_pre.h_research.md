# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/macos_carbon_pre.h

`macos_carbon_pre.h` is the non-debug CodeWarrior prefix header for Carbon builds. It only defines `__CARBON__`.

The generated CodeWarrior project script would use this for a final Carbon target. It has no includes or runtime logic, only compile-time platform selection.
