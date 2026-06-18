<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcdebug/rpcdebug.c -->
# sources/user-network-fs/nfs-utils/tools/rpcdebug/rpcdebug.c

## Purpose

`rpcdebug.c` implements a command-line tool for viewing, setting, and clearing Linux RPC/NFS/NFSD/NLM debug flag bitmasks exposed under `/proc/sys/sunrpc`.

## Important APIs, Types, and Functions

The `flagmap` table maps module/flag names to constants from `<nfs/debug.h>`. `find_flag` resolves names and detects ambiguous cross-module flags when no module is specified. `get_flags` and `set_flags` read/write `/proc/sys/sunrpc/<module>_debug`. `print_flags` formats active or all valid flags. `strtolower` lowercases names into a static buffer. `usage` prints command help. `main` parses `-c`, `-s`, `-m`, `-v`, and program-name aliases `nfsdebug`/`nfsddebug`.

## Control Flow

The tool determines a default module from argv[0] aliases, validates at most one of clear/set modes, resolves any supplied flags, defaults to showing all current flags when no flags are specified, reads the current bitmask, optionally writes a set or cleared bitmask, then prints resulting active flags and optionally the valid flag list.

## State and Persistence Behavior

It persists no user files. Writing debug masks changes live kernel sysctl state under `/proc/sys/sunrpc`, which remains until changed again or reset by kernel/module lifecycle.

## Dependencies and Integration Points

It depends on Linux proc sysctl files and NFS debug constants. It integrates with kernel RPC/NFS debugging for administrators and can be symlinked/renamed to default specific modules.

## Risks and Edge Cases

Writes require privileges and procfs support. `strtolower` uses a 64-byte static buffer and `strcpy`, so unexpectedly long names would overflow, though table/module names are controlled. `cdename` is allocated but never freed. The value is written with `%d` despite unsigned semantics. Flag aliases with duplicate values are suppressed unless `show_all`.

## Test Signals

Tests should mock proc sysctl files, verify module validation, alias behavior, ambiguous flag detection, set/clear masks, verbose valid flag output, unknown names, short writes, and permission/read errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcdebug/rpcdebug.c -->
