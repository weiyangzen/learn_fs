# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/9660/direc.c

In-memory directory tree management for ISO image construction.

`mkdirec` initializes a `Direc` from an `XDir`. Children are kept sorted by UTF name while building. `dbsearch` performs binary search by name segment, `walkdirec` resolves slash-separated paths, and `adddirec` inserts a file or directory, requiring intermediate directories to already exist.

`copydirec` recursively copies a tree, used for building a Joliet tree from the ISO tree after file blocks are assigned. `checknames` marks nodes with `Dbadname` when a supplied predicate rejects the name, and always marks `_conform.map` bad. `convertnames` assigns `confname`, either by conform-map generated names or a supplied conversion function such as `struprcpy`/`strcpy`. `dsort` recursively sorts child arrays with ISO or Joliet comparison functions.

Integration points: populated by `dump9660.c` from proto files and used by write/path/boot/dump modules.

Risks and notes: after `dsort`, `adddirec` should not be used because build-order sort assumptions change. Path insertion mutates the input string temporarily around the last slash.
