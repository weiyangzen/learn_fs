# File Research: sources/os/bsd/openbsd-src/sbin/restore/dirs.c

## Purpose

Directory handling for `restore`. It extracts directory records from dump tapes into temporary files, builds an inode-to-directory table, supports pathname lookup and recursive tree scans, and later restores directory metadata.

## Directory Extraction

`extractdirs()` creates a temporary directory file and optional mode file under `tmpdir`, then reads directory files from the tape while `curfile` is a directory. Each directory gets an `inotab` entry with its seek offset. Directory payload is passed through `getfile(putdir, xtrnull)`, normalized into `struct direct` records, terminated with a synthetic zero-inode `/` record, and sized by the resulting seek offset. If mode generation is enabled, `allocinotab()` writes owner, mode, flags, and access/modify/birth times to the mode file.

`skipdirs()` skips directory entries on tape without extracting them.

## Virtual Directory API

The file defines `RST_DIR`, `rst_opendir()`, `rst_readdir()`, and `rst_closedir()` over the temporary directory file. `rst_seekdir()` and `rst_telldir()` support repeated scans of many directories packed into one file. `rst_readdir()` reads fixed `DIRBLKSIZ` blocks, validates record lengths, treats the synthetic `/` marker as end of directory, rejects out-of-range inode numbers, and returns direct records.

## Lookup And Traversal

`pathsearch()` resolves absolute or relative canonical restore paths starting from `ROOTINO` by repeatedly calling `searchdir()`. `dirlookup()` is declared elsewhere and used by higher layers, while `treescan()` recursively walks the extracted directory hierarchy and calls a callback with `LEAF` or `NODE`. It skips `.` and `..`, guards against path overflow, and seeks back after recursive descent.

## Directory Record Conversion

`putdir()` supports old directory format conversion through `dcvt()` when `cvtflag` is set, byte-swaps fields when `Bcvt` is active, handles old inode format name-length quirks, validates record alignment/size/name length, and writes compacted records through `putent()` and `flushent()`.

## Metadata Restoration

`setdirmodes()` replays the mode file after extraction. It looks up each directory in the symbol table, skips existing interactive/batch directories unless forced, optionally asks before setting root metadata, and applies owner, mode, flags, and times unless `Nflag` dry-run mode is active.

## Other Helpers

`genliteraldir()` writes a literal copy of a dumped directory into a file named by inode when restore is in inode-name mode. `inodetype()` reports whether an inode has an `inotab` entry. `cleanup()` closes tape state and removes temp files.

## Risks And Invariants

- The temporary directory file is central to name-based restore; missing root directory is fatal.
- Path buffers are bounded, but long names may be skipped with warnings during traversal/listing.
- Directory entries from tape are partially trusted only after record-size validation; malformed records are skipped by block.
- `setdirmodes()` depends on symbol table entries created by extraction scheduling.
