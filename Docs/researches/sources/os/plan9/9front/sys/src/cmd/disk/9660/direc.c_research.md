# File Research: sources/os/plan9/9front/sys/src/cmd/disk/9660/direc.c

In-memory ISO directory tree construction and manipulation.

Key behavior:
- `mkdirec` converts an `XDir` into a `Direc`.
- `walkdirec` follows slash-separated paths through sorted child arrays.
- `adddirec` inserts a file or directory into a sorted child list, requiring intermediate directories to already exist.
- `copydirec` deep-copies directory subtrees.
- `checknames` marks non-conforming names and `_conform.map`.
- `convertnames` assigns each entry’s `confname`, using generated conform names for `Dbadname` entries.
- `dsort` recursively sorts the tree by ISO or Joliet comparison function.

Notable dependencies:
- Name validation/comparison from `ichar.c` and `jchar.c`.
- Conformance map from `conform.c`.

Research notes:
- `adddirec` mutates the path string temporarily when splitting parent path from basename.
- After `dsort`, callers must not use `adddirec` on that tree because the sort order may no longer match UTF-name insertion order.
