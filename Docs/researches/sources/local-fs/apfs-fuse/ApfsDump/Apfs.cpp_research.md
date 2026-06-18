# File Research: sources/local-fs/apfs-fuse/ApfsDump/Apfs.cpp

This is the `apfs-dump` command-line entry point. The active `main()` parses `-map`, `-fusion`, main/tier2 device paths, and output path, opens devices through `Device::OpenDevice`, initializes a `Dumper`, optionally writes a block map, and then dumps the container.

It defines the global interrupt flag `g_abort` and installs a Ctrl-C handler on Linux/macOS so long block scans can abort cooperatively. It also sets `g_debug = 255`, so dump runs enable broad diagnostic output.

The lower half is the active implementation; the earlier large `#if 0` block preserves older direct scan helpers (`MapBlocks`, `ScanBlocks`, `DumpSpaceman`) and an obsolete main path. Those disabled helpers show the historical design: raw block verification plus `BlockDumper` dispatch.

Key dependencies are `Device`, `GptPartitionMap`, `Util`, `DiskStruct`, `BlockDumper`, and local `Dumper`. The file owns CLI orchestration, not APFS parsing itself.

Notable risks: argument parsing is manual and order-sensitive; fusion mode changes positional parsing. `g_debug` is forced globally, so this tool is intentionally verbose and not a quiet library-style consumer.
