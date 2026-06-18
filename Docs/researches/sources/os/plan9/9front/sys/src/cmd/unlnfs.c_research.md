# File Research: sources/os/plan9/9front/sys/src/cmd/unlnfs.c

`unlnfs` restores long filenames from a `.longnames` file. It reads long names, computes each name’s encoded MD5-derived short name with `enc32`, then recursively walks a directory and renames any entry whose name matches the 26-character encoded form.

The mapping list is stored as linked `Name` records. `renamedir()` descends into subdirectories before checking entries for rename candidates. `rename()` uses `dirwstat()` to change the directory entry name.

It exits if `.longnames` cannot be opened. Memory/error handling is minimal but consistent with a small Plan 9 utility.
