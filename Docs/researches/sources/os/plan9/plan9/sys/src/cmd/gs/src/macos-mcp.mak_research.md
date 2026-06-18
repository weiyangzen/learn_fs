# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/macos-mcp.mak

`macos-mcp.mak` generates a CodeWarrior XML project from a Unix/Darwin make run. It is not intended to compile Ghostscript directly with CodeWarrior during this make pass; it sets `CC=echo` so object names can be collected, while auxiliary generators are built with `cc`.

The options configure source/object/generated directories, runtime library paths, Mac OS platform identity, third-party library locations, non-shared bundled library use, classic Mac features, device sets, file/stdio implementations, and no-sync threading. It includes the normal Ghostscript make fragments (`gs.mak`, `lib.mak`, `int.mak`, third-party library makefiles, device makefiles, and `unix-end.mak`) to produce the same dependency graph.

The file adds Mac-specific device and platform module rules for `gdevmac`, `gp_mac`, `gp_macio`, `gp_stdin`, `gp_getnv`, `gp_nsync`, `gdevemap`, `gsdll`, and optional `gp_macpoll`. It also supplies rules for generated helper executables and an intentionally blank `gconfig_.h`.

The final project target copies `macsystypes.h` to `obj/sys/types.h`, runs `macgenmcpxml.sh` with the link trace to produce `ghostscript.mcp.xml`, copies generated configuration source stubs, and sets the Mac file type/creator with `/Developer/Tools/SetFile`. This is fragile historical build glue and depends on old Darwin/CodeWarrior tooling.
