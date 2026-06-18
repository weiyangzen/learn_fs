# File Research: sources/local-fs/udftools/wrudf/wrudf.c

## Purpose

`wrudf.c` is the main program for the interactive `wrudf` tool. It defines global process state, initializes the target UDF volume, opens the volume for modification, runs the command loop, and finalizes metadata updates before closing.

## Global State

The file owns key globals declared in `wrudf.h`:

- Device state: `devicename`, `device`, `devicetype`, `medium`, and `ignoreReadError`.
- Command parser state: `line`, `cmndc`, `cmndvSize`, `cmndv`, and `options`.
- Descriptor discovery bitmask `found`.
- Directory state: `rootDir`, `curDir`, and global `timeStamp`.
- UDF descriptors/extents: main/reserve/next volume descriptor sequence extents, logical volume integrity sequence state, `pd`, `lvd`, `usd`, `spaceMap`, `lvid`, `fsd`, `st`, `vat`, and `virtualPartitionNum`.
- Dirty flags for space bitmap, USD, and sparing table.
- `entityWRUDF`, the implementation identifier written into metadata.

## Initialization Flow

`initialise()` begins by calling `initIO()`, then reads and validates the UDF Volume Recognition Sequence from blocks 16 through 255, accepting `BEA01`, `NSR02`, and `TEA01`.

It locates the Anchor Volume Descriptor Pointer:

- CD-R requires an AVDP at block 512.
- Other media try block 256, then `trackSize - 1`, then `trackSize - 256`.

It reads the Volume Descriptor Sequence, following `TAG_IDENT_VDP` continuations, selecting prevailing descriptors by volume descriptor sequence number:

- Primary Volume Descriptor presence is noted.
- The writable Partition Descriptor is stored for rewritable or write-once access types.
- The Logical Volume Descriptor is stored.
- The Unallocated Space Descriptor is stored when present.

The code requires a Logical Volume Descriptor, Partition Descriptor, and 2048-byte logical block size.

## Partition Maps And VAT

`initialise()` walks LVD partition maps:

- A sparable partition map loads the first sparing table copy and counts used entries.
- A virtual partition map records `virtualPartitionNum`.

For CD-R, a virtual partition map is mandatory and `readVATtable()` loads the VAT. For non-CD-R media, an Unallocated Space Descriptor is mandatory.

## Fileset, Space Bitmap, And Integrity Sequence

The File Set Descriptor sequence is read from `lvd->logicalVolContentsUse`, and the prevailing FSD is copied. The unallocated space bitmap is loaded from the partition header descriptor when present.

The user is prompted to confirm updates to the decoded file set identifier. After confirmation, the Logical Volume Integrity Descriptor sequence is read, following continuation extents if present. A closed CD-R volume is rejected.

For CD-R, the logical volume header unique ID is restored from the VAT file entry's unique ID. For CD-RW, if the LVID is already open, the user is prompted before proceeding.

For rewritable media, the code reserves/sets up the next LVID location, marks the current LVID open, writes it into the packet cache, and records a continuation extent if the integrity sequence is near exhaustion.

Finally it creates the root `Directory` structure and loads the root directory with `readDirectory()`.

## Finalization

`finalise()` flushes dirty directories first. Then:

- On CD-R, it writes a new VAT table with `writeVATtable()`.
- On CD-RW, it rewrites the space bitmap if dirty, writes sparing tables if dirty, writes a closed LVID, writes a terminating descriptor, and rewrites dirty USD data in both main and reserve volume descriptor sequences.

It then calls `closeIO()` and frees allocated descriptor/global buffers.

## Command Parsing

`parseCmnd()` tokenizes an input line in place, recognizes `cp`, `rm`, `mkdir`, `rmdir`, `lsc`, `lsh`, `cdc`, `cdh`, `quit`, `exit`, and `help`, and rejects ambiguous `cd`/`ls` in favor of explicit harddisk or compact-disc commands.

It supports double-quoted arguments in a limited way, parses `-f` and `-r` options into the global `options` bitmask, removes option entries from `cmndv`, and returns a command enum or error code.

## Main Loop

`main()` sets locale, prints version, chooses `/dev/cdrom` unless one device/image argument is supplied, tries to raise priority, records the current host working directory, initializes the volume, and enters an interactive prompt loop.

The prompt is built from the current UDF directory chain. Each parsed command dispatches to the corresponding command handler in `wrudf-cmnd.c`. Return values are translated into user-facing messages. `quit` or `exit` breaks the loop, frees `hdWorkingDir`, and calls `finalise()`.

## Notable Details

The program is intentionally interactive and asks for confirmation before modifying the volume. It supports disk images and real optical media through the same global I/O interfaces.

`parseCmnd()` mutates the input line and has limited quote handling; it does not implement escaping. The readline and non-readline paths differ in line storage but share the same parser.
