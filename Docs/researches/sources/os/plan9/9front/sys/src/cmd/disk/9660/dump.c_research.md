# File Research: sources/os/plan9/9front/sys/src/cmd/disk/9660/dump.c

Incremental dump-CD metadata and content-deduplication support.

Key behavior:
- Computes MD5 digests of existing CD file extents and indexes them by both digest and block number.
- `dumpcd` walks existing dump day directories and records file content for deduplication.
- `lookupmd5` and `insertmd5` support reusing existing extents when new input content matches old content.
- `readkids` parses directory blocks into child `Direc` arrays.
- `adddumpdir` creates year/day dump directory names based on local time, adding numeric suffixes for duplicates.
- `Cputdumpblock` writes a special `plan 9 dump cd` marker block.
- `hasdump`, `readdumpdirs`, and `readdumpconform` walk the linked dump-block chain and reconstruct dump roots plus conform-name mappings.

Notable dependencies:
- MD5 from `libsec`.
- Directory parsing and block I/O from `cdrdwr.c`.

Research notes:
- The dump block chain is the commit log for append/update operations; the old null header is rewritten last to commit changes.
- Duplicate content on CD is warned about but can be used for extent reuse.
