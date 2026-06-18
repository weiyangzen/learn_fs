<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/mount.h -->
# sources/user-network-fs/cifs-utils/mount.h

## Purpose

`mount.h` centralizes mount-helper exit status bits, mtab path helpers, and mtab function prototypes.

## Important APIs, Types, and Functions

It defines `EX_USAGE`, `EX_SYSERR`, `EX_SOFTWARE`, `EX_USER`, `EX_FILEIO`, `EX_FAIL`, `EX_SOMEOK`, `_PATH_MOUNTED_LOCK`, `_PATH_MOUNTED_TMP`, and prototypes for `mtab_unusable`, `lock_mtab`, `unlock_mtab`, and `my_endmntent`.

## Control Flow

There is no executable flow. `mount.cifs.c`, resolver code, and credential tools use the exit constants for consistent error reporting.

## State and Persistence Behavior

The mtab path macros describe filesystem lock/temp state used by `mtab.c`.

## Dependencies and Integration Points

It relies on `_PATH_MOUNTED` from system path headers included by consumers. It integrates `mount.cifs.c` with `mtab.c`.

## Risks and Edge Cases

Exit constants are bit flags, but many callers return them as discrete values. Path macros inherit platform-specific `_PATH_MOUNTED` behavior.

## Test Signals

Compile tests and mtab update tests should ensure prototypes and constants match implementations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/mount.h -->
