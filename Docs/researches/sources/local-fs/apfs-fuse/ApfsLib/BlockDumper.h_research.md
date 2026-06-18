# File Research: sources/local-fs/apfs-fuse/ApfsLib/BlockDumper.h

This header declares `FlagDesc` and `BlockDumper`.

Public API is small: constructor, destructor, text-flag setter, block-size getter/setter, `DumpNode()`, stream accessor, and static `GetNodeType()`. The rest is private dump dispatch and formatting machinery.

Private methods include block dumpers for APFS/NX object types, B-tree node/entry dumpers for known subtypes, xfield dumping, hex dumping, flag/enum formatting, timestamp formatting, and typed field printers.

State consists of APFS text flags, output stream reference, current block pointer, and current block size. It is not thread-safe and is designed for synchronous diagnostic rendering.
