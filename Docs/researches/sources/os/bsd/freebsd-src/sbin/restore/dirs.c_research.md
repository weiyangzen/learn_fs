# File Research: sources/os/bsd/freebsd-src/sbin/restore/dirs.c

Purpose: builds and queries restore’s temporary directory database while reading dump tapes. It records dumped directory contents in `dirfile`, optional directory metadata and extended attributes in `modefile`, and maps directory inode numbers to offsets through a hashed `inotab`.

Key functions:
- `extractdirs()` consumes directory records from tape, writes normalized directory entries to a temporary database, optionally records `modeinfo`, and validates that the root directory exists.
- `treescan()` recursively walks the dump directory tree and calls a supplied callback for each pathname/inode.
- `pathsearch()`, `searchdir()`, `rst_opendir()`, `rst_readdir()`, and `rst_closedir()` provide a small directory API over the temporary dump-directory file.
- `setdirmodes()` replays directory ownership, mode, timestamps, flags, and extended attributes after extraction.
- `genliteraldir()` writes a literal copy of a dumped directory file when restore is running inode-number mode.
- `done()` closes tape input and removes temporary directory/mode files.

Integration: depends on `getfile()`, `skipfile()`, `curfile`, `dumpmap`, `lookupino()`, `myname()`, and `set_extattr()` from the rest of restore. It is central to name-based restore because later selection and extraction operate against this synthesized directory view.

Risk notes: path handling uses fixed `MAXPATHLEN` buffers and some unchecked `strcpy()` paths, assuming caller-normalized input. Directory-entry validation attempts to skip malformed records, but corrupted dump input can still affect traversal and warnings. Temporary file failures are fatal through `fail_dirtmp()`.
