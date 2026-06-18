# File Research: sources/local-fs/udftools/wrudf/wrudf.h

## Purpose

`wrudf.h` is the central internal header for the `wrudf` program. It includes UDF/ECMA structure headers, declares global state shared by all wrudf source files, defines command/result enums and option bits, defines the in-memory directory cache structure, and declares cross-file functions.

## Included Interfaces

The header includes:

- Standard time/string/integer headers.
- `ecma_167.h`, `osta_udf.h`, and `libudffs.h`, which provide the UDF descriptor structures, constants, CRC/string helpers, and allocation descriptor types used throughout these files.

It defines `struct generic_desc` as a common prefix for tagged descriptors with `descTag` and `volDescSeqNum`.

## Shared Global State

The header declares globals for:

- Host working directory: `hdWorkingDir`.
- Device and mode: `ignoreReadError`, `device`, `devicetype`, `DISK_IMAGE`, `medium`, and `trackSize`.
- Command input: `line`, `cmndc`, `cmndv`, and `options`.
- Dirty metadata flags: `spaceMapDirty`, `usdDirty`, `sparingTableDirty`.
- Loaded UDF metadata: `lvd`, writable partition `pd`, `virtualPartitionNum`, `vat`, `usd`, `spaceMap`, `lvid`, `fsd`, `usedSparingEntries`, and `st`.
- Current implementation and timestamp: `entityWRUDF` and `timeStamp`.

The medium enum distinguishes `CDR` and `CDRW`; disk images are represented separately by `devicetype == DISK_IMAGE` while still emulating either medium behavior.

## Result And Command Enums

`enum RV` standardizes command return states such as `CMND_OK`, `CMND_FAILED`, bad argument counts, invalid directories, existing/deleted files or directories, permission denial, and directory/file type mismatches.

`enum CMND` assigns command IDs for `cp`, `rm`, `mkdir`, `rmdir`, compact-disc and harddisk list/change-directory operations, and quit.

Option bits include:

- `OPT_DUMMY`
- `OPT_FORCE`
- `OPT_RECURSIVE`

Only recursive behavior is materially used in this group.

## Directory Structure

`Directory` is the in-memory representation of a loaded UDF directory:

- `parent` and `child` model a single active directory chain.
- `dataSize` and `data` hold the linear FID byte stream.
- `icb` identifies the directory file entry.
- `name` is the decoded/local directory name.
- `dirDirty` tracks whether directory data/file entry must be rewritten.
- `fe[2048]` stores a copy of the directory's file entry block.

`rootDir` and `curDir` point into this chain.

## Cross-File Function Contracts

The header groups declarations by implementation file:

- `wrudf-cmnd.c`: directory update/read and command handlers.
- `wrudf-desc.c`: FID/FileEntry creation, lookup, insertion, and deletion.
- `wrudf-cdrw.c`: bitmap/extent allocation, timestamp/checksum helpers, address translation, sparing-table update, block and extent I/O, and device open/close.
- `wrudf-cdr.c`: VAT allocation, next-writable-address helpers, CD-R read/write/verify, and VAT table read/write.
- `ide-pc.h`: `fail()` declaration, with the detailed ATAPI/MMC command interface included separately by implementation files that need it.

## Notable Details

The header exposes many mutable globals rather than encapsulating volume/session state. This matches the small interactive utility design but tightly couples all source files and makes reentrancy or concurrent operation impossible.

`ABSOLUTE` uses `0xFFFF` as a sentinel partition number even though the comment notes it can be a valid UDF partition number.
