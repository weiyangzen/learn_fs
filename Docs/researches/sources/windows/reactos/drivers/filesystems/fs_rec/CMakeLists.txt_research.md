# File Research: sources/windows/reactos/drivers/filesystems/fs_rec/CMakeLists.txt

Build definition for the ReactOS filesystem recognizer driver. It appends the recognizer sources for block-device helpers and the individual filesystem probes (`btrfs`, `cdfs`, `ext`, `fat`, `fatx`, `ffs`, `ntfs`, `reiserfs`, `udfs`) plus `fs_rec.c` and `fs_rec.h`, builds them as the `fs_rec` kernel-mode driver module with `fs_rec.rc`, imports `ntoskrnl` and `hal`, enables `fs_rec.h` as the precompiled header, and installs the driver to `reactos/system32/drivers`.
