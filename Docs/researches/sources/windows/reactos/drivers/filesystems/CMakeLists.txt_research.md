# File Research: sources/windows/reactos/drivers/filesystems/CMakeLists.txt

Top-level ReactOS filesystem-driver build aggregator. It contains only `add_subdirectory()` entries and delegates all actual driver definitions to child directories.

Key behavior:
- Adds the Btrfs driver first, followed by CDFS, Ext2, FastFAT, filesystem recognizer, mailslot, MUP, NFS, named pipe, NTFS, UDFS, and VFAT filesystem driver subprojects.
- Has no conditional logic, target declarations, compiler options, or dependency wiring of its own.

Filesystem/build relevance:
- Defines which filesystem drivers are included beneath `drivers/filesystems` in this ReactOS build tree.
- The Btrfs subtree is part of the default filesystem-driver traversal through this file.

Notable risks:
- Build inclusion is all-or-nothing per listed subdirectory; disabling a driver requires editing this list or handling it in the child project.
