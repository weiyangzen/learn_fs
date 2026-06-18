# File Research: sources/local-fs/apfs-fuse/ApfsDumpQuick/ApfsDumpQuick.cpp

This is a second diagnostic CLI, `apfs-dump-quick`, built on the higher-level `ApfsContainer` and `ApfsVolume` APIs instead of the raw `Dumper` class. It accepts a main device, optional `-f` fusion device, and log output path.

The program opens devices, detects first APFS GPT partitions on main and tier2, initializes `ApfsContainer`, creates a `BlockDumper`, dumps the container, then iterates `NX_MAX_FILE_SYSTEMS` and dumps each mountable volume.

It sets `g_debug = 255` and prints discovered volume names to stdout. Most direct directory/file-read experimentation is preserved under `#if 0`, showing prior manual tests with `ApfsDir`.

Notable risks: if `argc < 5` in `-f` mode, it prints syntax but does not immediately return before using `argv[4]`. It closes only the main disk at the end; the tier2 device is managed by `unique_ptr` but its explicit `Close()` is not called.
