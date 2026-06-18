# File Research: sources/local-fs/apfs-fuse/ApfsLib/BlockDumper.cpp

`BlockDumper` is the central APFS diagnostic formatter. It maps APFS object types and B-tree subtypes to textual dumps, printing object headers, block-specific metadata, B-tree headers, entries, flags, timestamps, UUIDs, and trimmed hex dumps.

`DumpNode()` dispatches by `OBJECT_TYPE_MASK` to container superblocks, APFS volume superblocks, B-tree roots/nodes, spaceman/CAB/CIB/bitmap-related metadata, OMAP, checkpoint maps, reaper state, EFI jumpstart, Fusion writeback cache/list, encryption-rolling state, snapshot metadata extensions, and integrity metadata.

B-tree entry dumpers cover filesystem tree records, OMAP entries, physical extent refs, snapshot metadata/name records, OMAP snapshots, spaceman free queues, gbitmap records, Fusion middle tree records, sealed-volume fext tree records, and unknown entries.

Filesystem-tree formatting decodes inode records, xattrs including symlink/quarantine/decmpfs special cases, sibling links/maps, dstream IDs, crypto states, file extents, directory records, and file-info hashes. It also decodes APFS xfields for inodes and directory records.

The file contains extensive flag-description tables for APFS/NX/inode/xattr/B-tree/Fusion flags and helper formatters `flagstr`, `enumstr`, `GetNodeType`, `tstamp`, and overloaded `dumpm()` field printers.

Notable risks: this is diagnostic code and uses many `assert()` calls and direct struct casts. Unknown or malformed blocks may produce noisy output or hex dumps rather than robust error recovery.
