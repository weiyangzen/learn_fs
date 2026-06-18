# File Research: sources/windows/reactos/sdk/lib/fslib/CMakeLists.txt

Read completely: 7 lines.

This top-level fslib build file includes the filesystem utility subdirectories: `btrfslib`, `cdfslib`, `ext2lib`, `ntfslib`, `vfatlib`, and `vfatxlib`.

It has no logic beyond subdirectory aggregation, but it defines which filesystem format/check libraries are part of the ReactOS SDK build.

Security/reliability notes: no runtime behavior. Build coverage risk is limited to omitting or adding fslib modules.
