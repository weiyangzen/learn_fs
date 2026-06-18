# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/file.c

This file manages user-specified file actions for the FAT checker: drop, undelete, and matching by path/name.

Core responsibilities:
- `file_name` converts an 8.3 directory entry name into printable form.
- `file_cvt` converts a user path component to fixed 11-byte uppercase DOS name form, supporting octal escapes.
- `file_add` inserts a requested absolute path into an `FDSC` tree with action type.
- `file_cd` descends into a requested directory action subtree.
- `file_type` returns the requested action for a fixed filename.
- `file_modify` applies drop or undelete to a matched directory entry name.
- `file_unused` reports requested actions that were never matched and frees the action tree.

Risk points:
- Non-ReactOS allocation/free calls remain in this file (`alloc`, `free`) and are expected to be macro-adapted by included headers.
- `file_add` temporarily writes NUL bytes into the path string while parsing.
- Undelete matching treats deleted names specially by ignoring the first byte, which can be ambiguous.
- ReactOS builds do not enable interactive prompting, so this support is mostly driven by programmatic action lists.
