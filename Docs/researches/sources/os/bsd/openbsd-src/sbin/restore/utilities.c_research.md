# File Research: sources/os/bsd/openbsd-src/sbin/restore/utilities.c

This file provides filesystem-side helper operations for `restore`: path creation, temporary renaming, directory/leaf removal, link creation, inode search bounds, diagnostics, prompts, and panic handling.

Key APIs:
- `pathcheck()`: ensures all parent path components exist in the restore entry tree and creates missing directories.
- `mktempname()`, `gentempname()`, `renameit()`: create deterministic temporary names for conflicting entries and rename them on disk.
- `newnode()`, `removenode()`, `removeleaf()`: create or remove directories and leaf files with `Nflag` dry-run support.
- `linkit()`: creates symbolic or hard links.
- `lowerbnd()`, `upperbnd()`: find the next/previous inode that still needs extraction.
- `badentry()`, `flagvalues()`: print detailed restore tree diagnostics.
- `dirlookup()`, `reply()`, `panic()`: lookup dump pathnames, prompt the user, and handle inconsistencies.

Behavior and integration:
- Uses restore entry-tree helpers such as `lookupname`, `lookupino`, `pathsearch`, `addentry`, `myname`, `freename`, and `savename`.
- Honors global `Nflag`, `yflag`, `terminal`, `dumpmap`, and `maxino`.
- `panic()` is interactive unless `yflag` is set, in which case it returns to let the caller continue.

Risk notes:
- Several helpers temporarily mutate pathname strings while scanning components.
- `panic()` returning under `yflag` means callers must be robust after serious consistency errors.
- Temporary names are generated from link position and inode number, so correctness depends on entry-link list consistency.
