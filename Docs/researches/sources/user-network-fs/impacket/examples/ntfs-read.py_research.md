# sources/user-network-fs/impacket/examples/ntfs-read.py

## Purpose

`ntfs-read.py` is a read-only NTFS volume browser and extractor. It opens a raw NTFS volume or image, parses boot-sector, MFT, attribute, index, and filename structures, then provides an interactive mini-shell with `cd`, `ls`, `cat`, `hexdump`, and `get`. It can also extract a single path via `-extract`.

## Important APIs, Types, and Functions

The file defines many `impacket.structure.Structure` models: `NTFS_BPB`, `NTFS_EXTENDED_BPB`, `NTFS_BOOT_SECTOR`, `NTFS_MFT_RECORD`, resident and non-resident attribute records, filename attributes, index headers, index roots/allocation blocks, index entries, data runs, and attribute-list entries.

`Attribute`, `AttributeResident`, and `AttributeNonResident` parse generic attribute headers and data. `AttributeNonResident.parseDataRuns()` decodes NTFS runlists, including sparse runs and signed delta LCNs. `readVCN()` and `read()` translate logical offsets into clustered reads, clamp to `DataSize`, and zero-fill beyond `InitializedSize`. `NonResidentDataAttribute` merges multi-extent `$DATA` streams referenced by `$ATTRIBUTE_LIST`.

`INODE` parses standard information, filename, attribute list, index root, and index allocation; performs NTFS fixups; searches attributes locally and through attribute-list extension records; walks directory index roots and subnodes; resolves path components; and returns data streams. `NTFS` mounts the volume, computes record and index sizes from the BPB, reads the MFT, and returns parsed inodes. `MiniShell` exposes user commands over these primitives.

## Control Flow

`main()` initializes logging, creates `MiniShell(volume)`, and either issues `get <extract>` or enters `cmdloop()`. Mounting reads the boot sector, computes `$MFT` start, creates the root inode, and pre-populates tab completion with `ls`. Directory traversal starts from `$FILE_Root`, searches index entries by uppercase filename, loads child MFT records, and updates the prompt. File reads reject directories, compressed files, and encrypted files, then stream bytes from the default `$DATA` attribute in 40 KiB chunks to stdout, a hexdump callback, or an output file.

## State and Persistence Behavior

The volume is opened read-only (`rb`). Local state includes current inode, current NTFS path, cached completion entries, parsed attributes, and a volume file descriptor. The only write behavior is local extraction through `get`, which writes a file named by the basename of the requested NTFS path in the current local directory. Remote or on-volume state is never modified.

## Dependencies and Integration Points

The script depends on Impacket `Structure` and `hexdump`, Python `cmd`, `ntpath`, `struct`, and raw device/image file access. It is standalone within the Impacket examples but models NTFS structures taken partly from NTFS-3G. It integrates with OS raw device permissions for paths such as `\\.\C:` or `/dev/...`.

## Risks and Edge Cases

The parser is intentionally “quick and dirty” and does not support compressed or encrypted file data. It trusts many on-disk lengths and offsets, so corrupt volumes can cause short reads, parse errors, or loops. Attribute-list extension lookup can recurse through MFT records and may not handle all malformed or unusual split attributes. Directory search assumes NTFS collation ordering but has broad fallback traversal. `do_get()` opens the destination before validating the source, so a failed extraction can leave an empty local file. `main()` calls `sys.exit(1)` after successful completion, which reports failure to callers.

## Test Signals

Useful tests include fixture NTFS images with resident files, non-resident files spanning multiple data runs, sparse files, fragmented `$MFT`, split `$DATA` attributes, large directories using index allocation subnodes, DOS and Win32 filename variants, empty files, and corrupt fixup signatures. CLI smoke tests should cover `-extract`, shell `ls/cd/pwd/cat/hexdump/get`, and rejection of compressed/encrypted flags.
